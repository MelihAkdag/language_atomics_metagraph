"""End-to-end pipeline for knowledge graph construction from text."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from tqdm import tqdm
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

from core.utilities.Patterns import Action, ChainOfResponsibility
from cor.knowledge.Knowledge import Knowledge
from nlp.preprocessing.TextCleaner import TextCleaner
from nlp.extraction.SRLExtractor import SRLExtractor
from nlp.providers.factory import create_srl_provider, create_coref_resolver
from nlp.visualization.GraphBuilder import GraphBuilder

# Introducing a pipeline context to hold intermediate data
@dataclass
class NLPPipelineContext:
    """
    Context for NLP Pipeline processing.
    The chain (pipeline=chain of responsibility) does not pass outputs step-to-step via return values; it passes a mutable context.
    """
    raw_text: str
    db_name: str
    template: Optional[str]
    verbose: bool

    cleaned_text: str = ""
    doc: Any = None
    sentences: List[Any] = field(default_factory=list)
    srl_results: List[Dict[str, Any]] = field(default_factory=list)

    kb: Any = None


# Defining one Action per stage (in pipeline)

class CleanTextAction(Action):
    def __init__(self, pipeline: "KnowledgePipeline"):
        self.pipeline = pipeline

    def execute(self, ctxt: NLPPipelineContext):
        if ctxt.verbose:
            print("Cleaning text...")
            if self.pipeline.enable_coref:
                print(f"  Coreference strategy: {self.pipeline.coref_strategy}")

        ctxt.cleaned_text = self.pipeline.cleaner.clean(
            ctxt.raw_text,
            coref_resolver=self.pipeline.coref_resolver,
            coref_strategy=self.pipeline.coref_strategy,
            verbose=ctxt.verbose
        )


class ExtractSRLAction(Action):
    def __init__(self, pipeline: "KnowledgePipeline"):
        self.pipeline = pipeline

    def execute(self, ctxt: NLPPipelineContext):
        if ctxt.verbose:
            print("Extracting SRL...")

        results = self.pipeline.srl_provider.extract_primitives(ctxt.cleaned_text)

        ctxt.srl_results = [
            r for r in results
            if r.get("subjects") or r.get("objects")
        ]


class SaveToDatabaseAction(Action):
    def __init__(self, pipeline: "KnowledgePipeline"):
        self.pipeline = pipeline

    def execute(self, ctxt: NLPPipelineContext):
        if ctxt.verbose:
            print("Saving to database...")
        ctxt.kb = self.pipeline._save_to_database(ctxt.srl_results, ctxt.db_name, ctxt.template, ctxt.verbose)


class KnowledgePipeline:
    """Pipeline for extracting knowledge graphs from natural language text."""
    
    def __init__(self, model_name: str = "en_core_web_sm",
                 enable_coref: bool = True,
                 coref_strategy: str = 'replace',
                 srl_backend: str = "spacy",
                 coref_backend: str = "heuristic",
                 llm_client=None):
        """Initialize the pipeline.
        
        Args:
            model_name: spaCy model name to use
            enable_coref: Whether to enable coreference resolution
            coref_strategy: 'filter' to remove pronouns, 'replace' to substitute, 'none' to disable
            srl_backend: Backend for SRL extraction ('spacy' or 'llm')
            coref_backend: Backend for coreference resolution ('heuristic', 'llm', or 'none')
            llm_client: Optional LLM client for 'llm' backends
        """
        self.cleaner = TextCleaner()
        self.extractor = SRLExtractor(model_name)
        self.nlp = self.extractor.nlp
        
        self.srl_provider = create_srl_provider(srl_backend, extractor=self.extractor, llm_client=llm_client)

        self.enable_coref = enable_coref
        self.coref_strategy = coref_strategy

        self.coref_resolver = None
        if self.enable_coref:
            self.coref_resolver = create_coref_resolver(coref_backend, nlp=self.nlp, llm_client=llm_client)

    def process_text(
        self,
        text: str,
        db_name: str,
        template: Optional[str] = None,
        verbose: bool = True,
    ) -> Knowledge:
        """Process text and build a knowledge graph database."""
        ctxt = NLPPipelineContext(
            raw_text=text,
            db_name=db_name,
            template=template,
            verbose=verbose,
        )

        chain = ChainOfResponsibility.generate(
            [
                CleanTextAction(self),
                ExtractSRLAction(self),
                SaveToDatabaseAction(self),
            ]
        )
        chain.run(ctxt)

        if ctxt.kb is None:
            raise RuntimeError("Pipeline did not produce a Knowledge object.")
        return ctxt.kb



    def _save_to_database(self, srl_results: List[Dict[str, List[str]]],
                     db_name: str,
                     template: Optional[str],
                     verbose: bool) -> Knowledge:
        """Save SRL results to knowledge database.

        Args:
            srl_results: List of SRL extraction results
            db_name: Database name/path
            template: Optional template path
            verbose: Whether to show progress

        Returns:
            Populated Knowledge database
        """
        kb = Knowledge(db_name, template)
        say = kb.speak()

        iterator = tqdm(srl_results, desc="Saving to DB", unit="result") if verbose else srl_results

        for result in iterator:
            subjects = result['subjects']
            verb = result['verbs']
            objects = result['objects']
            anchors = result.get('anchors', [])
            inverse_relations = result.get('inverse_relations', [])
            possessive_relations = result.get('possessive_relations', [])

            for subject in subjects:
                for obj in objects:
                    if verb == "IS":
                        say.IS(subject, obj)
                    elif verb == "HAS":
                        # Use corresponding anchor if available
                        if len(anchors) >= 1:
                            for anchor in anchors:
                                for key, value in anchor.items():   # key=object, value=anchor attribute
                                    say.HAS(subject, value, key)
                        else:
                            say.HAS(subject, "HAS", obj)
                    elif verb == "HAS_INVERSE":
                        # Use corresponding anchor if available
                        if len(anchors) >= 1:
                            for anchor in anchors:
                                for key, value in anchor.items():   # key=object, value=anchor attribute
                                    say.HAS(key, value, subject)
                        else:
                            say.HAS(obj, "HAS", subject)
            
            # Handle inverse relations from prepositions
            for prep, pobj, obj in inverse_relations:
                # boston -> HAS -> laboratory (for "laboratory in Boston")
                say.HAS(pobj, prep, obj)
            
            # Handle possessive relations
            for poss_rel in possessive_relations:
                say.HAS(poss_rel["subject"], "HAS", poss_rel["object"])
        
        
                        ## Get or create vertices and assign values
                        #if subject not in STOP_WORDS:
                        #    subject_vertex = kb.graph.get_vertex_by_name(subject, auto_add=False)
                        #    if subject_vertex:
                        #        subject_vertex.set_value(100)
                        #if obj not in STOP_WORDS:
                        #    obj_vertex = kb.graph.get_vertex_by_name(obj, auto_add=False)
                        #    if obj_vertex:
                        #        obj_vertex.set_value(100)
                    
                        #say.HAS(subject, anchor, obj)
                        ## Get or create vertices and assign values
                        #if subject not in STOP_WORDS:
                        #    subject_vertex = kb.graph.get_vertex_by_name(subject, auto_add=False)
                        #    if subject_vertex:
                        #        subject_vertex.set_value(100)
                        #if anchor not in STOP_WORDS:
                        #    anchor_vertex = kb.graph.get_vertex_by_name(anchor, auto_add=False)
                        #    if anchor_vertex:
                        #        anchor_vertex.set_value(100)
                        #if obj not in STOP_WORDS:
                        #    obj_vertex = kb.graph.get_vertex_by_name(obj, auto_add=False)
                        #    if obj_vertex:
                        #        obj_vertex.set_value(100)

        return kb
    

    def visualize(self, 
                  db_name: str,
                  output_file: str, 
                  physics: bool = True,
                  vertex_query: Optional[str] = None,
                  arc_query: Optional[str] = None,) -> str:
        """Visualize knowledge graph from database.
        
        Args:
            db_name: Database name/path
            output_file: Output HTML filename
            physics: Whether to enable physics simulation
            vertex_query: Optional SQL query to filter vertices
            arc_query: Optional SQL query to filter arcs
            
        Returns:
            Absolute path to saved visualization
        """
        if vertex_query:
            print("Building graph from queries...")
            graph = GraphBuilder.build_from_query(db_name, vertex_query=vertex_query)
        elif arc_query:
            print("Building graph from queries...")
            graph = GraphBuilder.build_from_query(db_name, arc_query=arc_query)
        else:
            print("Building graph from database...")
            graph = GraphBuilder.build_from_database(db_name)
        return GraphBuilder.save_as_html(graph=graph, filename=output_file, physics=physics)






















