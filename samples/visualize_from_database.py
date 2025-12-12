import os
import sys

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from nlp.pipeline.knowledge_pipeline import KnowledgePipeline

def main():
    """Run the visualization from the existing knowledge database."""
    # Initialize pipeline
    pipeline = KnowledgePipeline()
    
    # Setup paths - use data directory structure
    project_root = os.path.join(os.path.dirname(__file__), '..')
    data_dir = os.path.join(project_root, 'data')
    
    # Load database
    template_path = os.path.join(project_root, 'tests', 'cor', 'knowledge', 'graph.s3db')
    db_path = os.path.join(data_dir, 'databases', 'db_frankenstein')
    
    # Visualize - save to data/visualizations
    html_path = os.path.join(data_dir, 'visualizations', 'frankenstein_knowledge_graph.html')
    
    # Select the arcs that connect important vertices
    arc_query = "SELECT id FROM arcs WHERE arcs.start IN (SELECT id FROM vertices WHERE value == 100) OR arcs.end IN (SELECT id FROM vertices WHERE value == 100)"
    pipeline.visualize(db_path, html_path, arc_query=arc_query)
    
    print("=" * 60)
    print("Visualization completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
