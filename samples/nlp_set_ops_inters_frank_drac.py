"""
Intersection of two NLP datasets (Frankenstein and Dracula) using Conception (a MetaGraph).

What this script does:
1) Loads two existing knowledge databases (SQLite .s3db files)
2) Builds two in-memory Conception graphs
3) Computes the intersection (shared concepts) using Conception's set operation
4) Saves the result to a new database
5) Visualizes the result as an HTML graph
"""

import os

from cor.knowledge.Knowledge import Knowledge
from cor.knowledge.Conception import Conception
from cor.knowledge.Concept import Concept
from nlp.pipeline.KnowledgePipeline import KnowledgePipeline


# ---------------------------
# 1) Choose your input/output files
# ---------------------------

FRANK_DB = r"data\databases\db_frankenstein"          # -> db_frankenstein.s3db
DRAC_DB = r"data\databases\db_dracula"               # -> db_dracula.s3db (make sure you created this)
OUT_DB = r"data\databases\db_frank_drac_intersection"  # -> db_frank_drac_intersection.s3db

OUT_HTML = r"data\visualizations\frank_drac_intersection.html"


def db_file_path(db_name: str) -> str:
    """Knowledge uses names like 'data\\databases\\db_xxx' but the real file is '...db_xxx.s3db'."""
    return db_name if db_name.lower().endswith(".s3db") else db_name + ".s3db"


def ensure_db_exists(db_name: str) -> None:
    path = db_file_path(db_name)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Couldn't find database file: {path}\n"
            f"Tip: Generate it first by running the matching pipeline sample."
        )


def load_conception_from_db(db_name: str) -> Conception:
    """
    Load a database and build a Conception in memory.

    Important note:
    - Each DB has its own numeric vertex IDs, so Frankenstein IDs won't match Dracula IDs.
    - Conception set operations compare vertex IDs.
    - So we rebuild Concept IDs from the *name* (Concept.to_id(name)), which is stable across DBs.
    """
    ensure_db_exists(db_name)

    kb = Knowledge(db_name)
    graph_id = kb.graph.id

    # We'll read the raw SQL tables directly to rebuild the graph.
    conn = kb.graph.conn.connect()
    cur = conn.cursor()

    conception = Conception()

    try:
        # ---- Load vertices ----
        cur.execute("SELECT id, name FROM vertices WHERE graph_id=?", (graph_id,))
        vertex_rows = cur.fetchall()

        # Map: database_vertex_id -> vertex_name
        dbid_to_name = {}
        for vid, name in vertex_rows:
            if name is None:
                continue
            dbid_to_name[int(vid)] = str(name)

        # Add every vertex (as a Concept) into our Conception
        for name in dbid_to_name.values():
            concept_vertex = Concept(name)  # stable ID derived from name
            conception.add(concept_vertex)

            # set a root if we don't have one yet (not super important for set ops)
            if conception.root is None:
                conception.root = concept_vertex

        # ---- Load arcs (edges) ----
        cur.execute(
            "SELECT id, name, weight, guid, start, end, anchor "
            "FROM arcs WHERE graph_id=?",
            (graph_id,),
        )
        arc_rows = cur.fetchall()

        for arc_id, arc_name, weight, guid, start_id, end_id, anchor_id in arc_rows:
            start_name = dbid_to_name.get(int(start_id)) if start_id is not None else None
            end_name = dbid_to_name.get(int(end_id)) if end_id is not None else None

            # If we can't resolve endpoints, skip
            if not start_name or not end_name:
                continue

            # Anchor is optional. We store it as a *name* to keep it simple.
            anchor_name = None
            if anchor_id and int(anchor_id) in dbid_to_name:
                anchor_name = dbid_to_name[int(anchor_id)]

            # Add the arc to the Conception
            conception.join(
                start_name,
                end_name,
                weight=float(weight or 0.0),
                name=str(arc_name or ""),
                anchor=anchor_name,
                guid=guid,
                aid=int(arc_id),
            )

        return conception

    finally:
        try:
            cur.close()
        except Exception:
            pass


def count_arcs(conception: Conception) -> int:
    """Just a small helper to print counts."""
    total = 0
    for v in conception.vertices.values():
        total += len(v.arcs)
    return total


def save_conception_to_new_db(conception: Conception, out_db_name: str) -> None:
    """
    Save the intersection conception into a new Knowledge database.

    - This saves vertices and arcs.
    - It also tries to save anchor links, but if you don't care, you can ignore that part.
    """
    # Optional: delete old output DB (so you can re-run easily)
    out_path = db_file_path(out_db_name)
    if os.path.exists(out_path):
        os.remove(out_path)

    # Use the template DB if it exists
    template = r"templates\graph.s3db"
    template = template if os.path.exists(template) else None

    out_kb = Knowledge(out_db_name, template=template)

    # 1) Save vertices
    for v in conception.vertices.values():
        out_kb.graph.get_vertex_by_name(
            v.name,
            vert_type=Concept.to_id(v.name),
            guid=v.guid,
            value=v.weight,
            auto_add=True,
        )

    # 2) Save arcs
    for v in conception.vertices.values():
        for a in v.arcs:
            arc_obj = out_kb.graph.join(
                a.start.name,
                a.end.name,
                arc_type=0,
                guid=a.guid,
                name=a.name,
                weight=a.weight,
            )

            # Save anchor if it exists (optional)
            if a.anchor:
                anchor_name = a.anchor.name if hasattr(a.anchor, "name") else str(a.anchor)
                anchor_vertex = out_kb.graph.get_vertex_by_name(
                    anchor_name,
                    vert_type=Concept.to_id(anchor_name),
                    auto_add=True,
                )
                try:
                    arc_obj["anchor"] = anchor_vertex.id
                except Exception:
                    pass


def main() -> None:
    # ---------------------------
    # 2) Load both datasets into Conception graphs
    # ---------------------------
    frank = load_conception_from_db(FRANK_DB)
    drac = load_conception_from_db(DRAC_DB)

    print("Loaded graphs:")
    print(f"  Frankenstein: {len(frank.vertices)} vertices, {count_arcs(frank)} arcs")
    print(f"  Dracula:      {len(drac.vertices)} vertices, {count_arcs(drac)} arcs")

    # ---------------------------
    # 3) Intersection set operation
    # ---------------------------
    inter = frank.intersection(drac)

    print("Intersection result:")
    print(f"  Intersection: {len(inter.vertices)} vertices, {count_arcs(inter)} arcs")

    # ---------------------------
    # 4) Save as a new dataset
    # ---------------------------
    save_conception_to_new_db(inter, OUT_DB)
    print(f"Saved intersection database: {db_file_path(OUT_DB)}")

    # ---------------------------
    # 5) Visualize the resulting dataset
    # ---------------------------
    pipeline = KnowledgePipeline()
    pipeline.visualize(db_name=OUT_DB, output_file=OUT_HTML)
    print(f"Wrote visualization HTML: {OUT_HTML}")


if __name__ == "__main__":
    main()