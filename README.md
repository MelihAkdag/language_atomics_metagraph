# language_atomics_metagraph

Repository to explore atomics of language as knowledge primitives.

## Quick Setup

### 1. Install Python 3.10 or later

- [Download Python](https://www.python.org/downloads/) and install it (add to PATH)

### 2. Clone the repository

```bash
git clone https://github.com/MelihAkdag/language_atomics_metagraph.git
cd language_atomics_metagraph
```

### 3. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Download spaCy language model

```bash
python -m spacy download en_core_web_sm
```

## Usage

### Run Example Pipeline

```bash
python examples/nlp_usage_examples.py
```

### Run Tests

```bash
python tests/nlp/test_text_cleaner.py
python tests/nlp/test_nlp_pipeline.py
```

## Project Structure

```
language_atomics_metagraph/
├── src/                          # Main source code
│   ├── cor/                      # Concept of Reasoning (CoR)
│   │   ├── knowledge/            # Knowledge representation primitives
│   │   │   ├── Concept.py        # Fundamental concept structures
│   │   │   ├── Conception.py     # Conception relationships
│   │   │   ├── Knowledge.py      # Knowledge base management
│   │   │   └── Language.py       # Language interface for knowledge
│   │   └── metagraph/            # Metagraph structures
│   │       ├── MetaGraph.py      # Graph representation
│   │       └── MetaGraphDatabase.py  # Database integration
│   │
│   ├── core/                     # Core utilities and infrastructure
│   │   └── utilities/            # Common utility modules
│   │       ├── ActiveRecord.py   # Database active record pattern
│   │       ├── GraphDatabase.py  # Graph database operations
│   │       ├── InvertedIndex.py  # Search indexing
│   │       ├── PropertySet.py    # Property management
│   │       └── Tree.py           # Tree data structures
│   │
│   └── nlp/                      # Natural Language Processing
│       ├── preprocessing/        # Text preprocessing
│       │   └── text_cleaner.py   # Text cleaning utilities
│       ├── extraction/           # Information extraction
│       │   └── srl_extractor.py  # Semantic Role Labeling
│       ├── visualization/        # Graph visualization
│       │   └── graph_builder.py  # Knowledge graph visualization
│       └── pipeline/             # End-to-end pipelines
│           └── knowledge_pipeline.py  # Complete extraction pipeline
│
├── data/                         # Data files (not tracked in git)
│   ├── raw/                      # Original datasets (e.g., frankenstein.txt)
│   ├── processed/                # Cleaned/transformed data
│   ├── databases/                # Generated SQLite databases (.s3db)
│   └── visualizations/           # HTML graph visualizations
│
├── examples/                     # Example usage scripts
│   └── nlp_usage_examples.py     # NLP pipeline demonstrations
│
└── tests/                        # Unit and integration tests
    ├── cor/                      # Tests for concept reasoning modules
    └── nlp/                      # Tests for NLP modules
```

### Key Modules

- **cor/** (Concept of Reasoning): Core knowledge representation using concepts, conceptions, and language primitives
- **core/**: Infrastructure utilities for database operations, indexing, and data structures
- **nlp/**: Natural language processing pipeline for extracting knowledge from text
- **data/**: All input/output data organized by type (raw → processed → databases → visualizations)
- **examples/**: Ready-to-run scripts demonstrating module usage
- **tests/**: Comprehensive test suite for all modules

## Adding New Dependencies

```bash
pip install <package-name>
pip freeze > requirements.txt
```

---

For more details, see the comments in each folder and script.
