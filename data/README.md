# Data Directory

This directory contains all datasets, databases, and generated outputs.

## Structure

```
data/
├── raw/                    # Raw input data (text files, CSVs, etc.)
│   └── frankenstein.txt    # Example: Frankenstein novel text
├── processed/              # Processed/cleaned data ready for analysis
├── databases/              # SQLite database files (.s3db, .db)
│   ├── db_frankenstein.s3db
│   └── example_output_db.s3db
└── visualizations/         # Generated HTML visualizations
    ├── frankenstein_knowledge_graph.html
    └── example_graph.html
```

## Directory Purposes

### `raw/`
- Contains original, unmodified datasets
- Text files, CSV files, JSON files, etc.
- This data should never be modified directly
- Examples: frankenstein.txt, other source texts

### `processed/`
- Contains cleaned, transformed, or preprocessed data
- Data that's been cleaned but not yet loaded into databases
- Intermediate data files from processing pipelines

### `databases/`
- SQLite database files (.s3db, .db)
- Knowledge graphs stored as relational databases
- Both template databases and populated databases

### `visualizations/`
- HTML graph visualizations
- Charts, plots, and other visual outputs
- Interactive network graphs from pyvis

## Usage

### Adding New Raw Data
```python
# Place raw text files in data/raw/
data_path = os.path.join(project_root, 'data', 'raw', 'my_text.txt')
```

### Saving Databases
```python
# Save databases to data/databases/
db_path = os.path.join(project_root, 'data', 'databases', 'my_db')
```

### Saving Visualizations
```python
# Save HTML visualizations to data/visualizations/
html_path = os.path.join(project_root, 'data', 'visualizations', 'my_graph.html')
```

## Git Configuration

The `.gitignore` is configured to:
- Track the directory structure (keep empty directories with `.gitkeep`)
- Ignore large database files (`*.s3db`, `*.db`)
- Ignore generated HTML visualizations (`*.html`)
- Keep small example files for documentation

## Best Practices

1. **Raw data should be immutable** - Never modify files in `raw/`
2. **Use descriptive names** - Name files clearly (e.g., `frankenstein_db` not `db1`)
3. **Document your data** - Add notes about data sources in comments
4. **Separate concerns** - Keep raw data, databases, and outputs in their respective folders
5. **Version control** - Small datasets can be tracked, but exclude large files
