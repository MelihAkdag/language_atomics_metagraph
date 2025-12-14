# Examples

This directory contains example scripts demonstrating how to use the various modules in the project.

## Available Examples

### `nlp_usage_examples.py`

Comprehensive examples of the NLP module functionality, including:

1. **Text Cleaning** - Using `TextCleaner` to normalize text
2. **Semantic Role Labeling** - Using `SRLExtractor` to extract subjects, verbs, and objects
3. **Complete Pipeline** - Using `KnowledgePipeline` for end-to-end processing

#### Running the Examples

```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Run all examples
python examples\nlp_usage_examples.py
```

#### What It Does

The script will:
- Demonstrate text cleaning with line breaks and multiple spaces
- Extract semantic roles from sample sentences
- Process sample text through the complete pipeline
- Generate a knowledge graph database in `data/databases/`
- Create an HTML visualization in `data/visualizations/`

#### Output Files

All output files are saved to the `data/` directory:
- Database: `data/databases/example_output_db.s3db`
- Visualization: `data/visualizations/example_graph.html`

## Adding New Examples

When creating new example scripts:

1. Place the script in this `samples/` directory
2. Use the data directory structure for inputs/outputs:
   - Load data from `data/raw/`
   - Save databases to `data/databases/`
   - Save visualizations to `data/visualizations/`
3. Add documentation to this README
4. Include clear comments explaining each step


## Best Practices

1. **Keep examples simple** - Focus on demonstrating one concept at a time
2. **Use sample data** - Create small test datasets for quick execution
3. **Document outputs** - Explain what files are created and where
4. **Add error handling** - Make examples robust and educational
5. **Follow data structure** - Always use the `data/` directory organization
