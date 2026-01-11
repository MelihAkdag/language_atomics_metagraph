from .contracts import SRLProvider, CorefResolver
from .spacy_backends import SpacySRLProvider, HeuristicCorefProvider
from .factory import create_srl_provider, create_coref_resolver