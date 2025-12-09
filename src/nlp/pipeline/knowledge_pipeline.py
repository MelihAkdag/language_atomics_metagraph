"""End-to-end pipeline for knowledge graph construction from text."""

from typing import List, Dict, Any, Optional
from tqdm import tqdm
import spacy

from cor.knowledge.Knowledge import Knowledge
from nlp.preprocessing.text_cleaner import TextCleaner
from nlp.extraction.srl_extractor import SRLExtractor
from nlp.visualization.graph_builder import GraphBuilder


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
            indirect_objects = result['indirect_objects']
            
            for subject in subjects:
                for verb in verbs:
                    for obj in objects:
                        if verb == "IS":
                            say.IS(subject, obj)
                        elif verb == "HAS":
                            say.HAS(subject, obj, f"{subject}.{obj}")
                    
                    for ind_obj in indirect_objects:
                        if verb == "IS":
                            say.IS(subject, ind_obj)
                        elif verb == "HAS":
                            say.HAS(subject, ind_obj, f"{subject}.{ind_obj}")
        
        return kb
    
    def visualize(self, db_name: str, output_file: str) -> str:
        """Visualize knowledge graph from database.
        
        Args:
            db_name: Database name/path
            output_file: Output HTML filename
            
        Returns:
            Absolute path to saved visualization
        """
        graph = GraphBuilder.build_from_database(db_name)
        return GraphBuilder.save_as_html(graph, output_file)
