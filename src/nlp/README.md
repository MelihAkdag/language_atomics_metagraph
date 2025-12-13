# NLP Module

Natural Language Processing module for knowledge extraction and graph construction.

## Structure

```
nlp/
├── __init__.py              # Package initialization
├── preprocessing/           # Text preprocessing utilities
│   ├── __init__.py
│   └── TextCleaner.py     # Text cleaning and normalization
├── extraction/             # Information extraction
│   ├── __init__.py
│   └── SRLExtractor.py    # Semantic Role Labeling
├── visualization/          # Graph visualization
│   ├── __init__.py
│   └── GraphBuilder.py    # Knowledge graph visualization
└── pipeline/               # End-to-end pipelines
    ├── __init__.py
    └── KnowledgePipeline.py # Complete extraction pipeline
```

## Usage

### Basic Pipeline Usage

```python
from nlp.pipeline.KnowledgePipeline import KnowledgePipeline

# Initialize pipeline
pipeline = KnowledgePipeline()

# Process text
text = "The cat is on the mat. John has a dog."
kb = pipeline.process_text(text, "output_db", template="templates/graph.s3db")

# Visualize
pipeline.visualize("output_db", "graph.html")
```

### Using Individual Components

```python
from nlp.preprocessing.TextCleaner import TextCleaner
from nlp.extraction.SRLExtractor import SRLExtractor

# Clean text
cleaner = TextCleaner()
cleaned = cleaner.clean("Hello\nWorld    Test")

# Extract SRL
extractor = SRLExtractor()
result = extractor.extract_primitives("The cat is on the mat.")
```

## Features

- **Text Cleaning**: Remove line breaks, normalize spaces
- **SRL Extraction**: Extract subjects, verbs, objects using spaCy
- **Verb Categorization**: Map verbs to IS/HAS primitives
- **Knowledge Graph Construction**: Build graph databases from text
- **Interactive Visualization**: Generate HTML visualizations with pyvis

## Requirements

- spacy >= 3.0.0
- networkx >= 2.5
- pyvis >= 0.3.0
- tqdm >= 4.60.0

## Testing

Run unit tests:
```bash
python -m unittest tests/nlp/test_TextCleaner.py
python -m unittest tests/nlp/test_SRLExtractor.py
```

Run integration test:
```bash
python tests/nlp/test_nlp_pipeline.py
```

## Example Output

The pipeline processes natural language text through several stages:

1. **Text Cleaning**: Normalizes whitespace and formatting
2. **Sentence Splitting**: Uses spaCy to identify sentence boundaries
3. **SRL Extraction**: Identifies subjects, verbs, and objects
4. **Knowledge Graph Construction**: Builds graph with IS/HAS relationships
5. **Visualization**: Creates interactive HTML graph visualization

Example extraction:
- Input: "The cat is small."
- Output: `{subjects: ['cat'], verbs: ['IS'], objects: ['small']}`
- Graph: `cat --IS--> small`
