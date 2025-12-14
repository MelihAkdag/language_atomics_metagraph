"""End-to-end pipeline for knowledge graph construction from text."""

from typing import List, Dict, Any, Optional
from tqdm import tqdm
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

from cor.knowledge.Knowledge import Knowledge
from nlp.preprocessing.TextCleaner import TextCleaner
from nlp.extraction.SRLExtractor import SRLExtractor
from nlp.visualization.GraphBuilder import GraphBuilder


class KnowledgePipeline:
    """Pipeline for extracting knowledge graphs from natural language text."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the pipeline.
        
        Args:
            model_name: spaCy model name to use
        """
        self.cleaner = TextCleaner()
        self.extractor = SRLExtractor(model_name)
        self.nlp = self.extractor.nlp
    
    def process_text(self, text: str, 
                     db_name: str,
                     template: Optional[str] = None,
                     verbose: bool = True) -> Knowledge:
        """Process text and build knowledge graph.
        
        Args:
            text: Raw input text
            db_name: Name/path for the knowledge database
            template: Optional database template path
            verbose: Whether to show progress bars
            
        Returns:
            Populated Knowledge database object
        """
        # Step 1: Clean text
        if verbose:
            print("Cleaning text...")
        cleaned_text = self.cleaner.clean(text)
        
        # Step 2: Split into sentences
        if verbose:
            print("Processing sentences...")
        doc = self.nlp(cleaned_text)
        sentences = list(doc.sents)
        
        # Step 3: Extract SRL results
        srl_results = []
        iterator = tqdm(sentences, desc="Extracting SRL", unit="sentence") if verbose else sentences
        
        for sent in iterator:
            result = self.extractor.extract_primitives(sent.text)
            srl_results.append(result)
        
        # Step 4: Save to database
        if verbose:
            print("Saving to database...")
        kb = self._save_to_database(srl_results, db_name, template, verbose)
        
        return kb
    
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
            verbs = result['verbs']
            objects = result['objects']
            anchors = result.get('anchors', [])
            indirect_objects = result['indirect_objects']

            for subject in subjects:
                subject = subject.lower()
                for i, verb in enumerate(verbs):
                    # Direct objects
                    for j, obj in enumerate(objects):
                        obj = obj.lower()
                        if verb == "IS":
                            say.IS(subject, obj)
                            # Get or create vertices and assign values
                            if subject not in STOP_WORDS:
                                subject_vertex = kb.graph.get_vertex_by_name(subject, auto_add=False)
                                if subject_vertex:
                                    subject_vertex.set_value(100)
                            if obj not in STOP_WORDS:
                                obj_vertex = kb.graph.get_vertex_by_name(obj, auto_add=False)
                                if obj_vertex:
                                    obj_vertex.set_value(100)

                        elif verb == "HAS":
                            # Use corresponding anchor if available
                            anchor = anchors[j] if j < len(anchors) else "property"
                            anchor = anchor.lower()
                            say.HAS(subject, anchor, obj)
                            # Get or create vertices and assign values
                            if subject not in STOP_WORDS:
                                subject_vertex = kb.graph.get_vertex_by_name(subject, auto_add=False)
                                if subject_vertex:
                                    subject_vertex.set_value(100)
                            if anchor not in STOP_WORDS:
                                anchor_vertex = kb.graph.get_vertex_by_name(anchor, auto_add=False)
                                if anchor_vertex:
                                    anchor_vertex.set_value(100)
                            if obj not in STOP_WORDS:
                                obj_vertex = kb.graph.get_vertex_by_name(obj, auto_add=False)
                                if obj_vertex:
                                    obj_vertex.set_value(100)

                    # Indirect objects
                    for ind_obj in indirect_objects:
                        ind_obj = ind_obj.lower()
                        if verb == "IS":
                            say.IS(subject, ind_obj)
                            # Get or create vertices and assign values
                            if subject not in STOP_WORDS:
                                subject_vertex = kb.graph.get_vertex_by_name(subject, auto_add=False)
                                if subject_vertex:
                                    subject_vertex.set_value(100)
                            if ind_obj not in STOP_WORDS:
                                ind_obj_vertex = kb.graph.get_vertex_by_name(ind_obj, auto_add=False)
                                if ind_obj_vertex:
                                    ind_obj_vertex.set_value(100)
                        elif verb == "HAS":
                            # For indirect objects, use generic anchor
                            anchor = "property"
                            say.HAS(subject, anchor, ind_obj)
                            # Get or create vertices and assign values
                            if subject not in STOP_WORDS:
                                subject_vertex = kb.graph.get_vertex_by_name(subject, auto_add=False)
                                if subject_vertex:
                                    subject_vertex.set_value(100)
                            if anchor not in STOP_WORDS:
                                anchor_vertex = kb.graph.get_vertex_by_name(anchor, auto_add=False)
                                if anchor_vertex:
                                    anchor_vertex.set_value(100)
                            if ind_obj not in STOP_WORDS:
                                ind_obj_vertex = kb.graph.get_vertex_by_name(ind_obj, auto_add=False)
                                if ind_obj_vertex:
                                    ind_obj_vertex.set_value(100)

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






















