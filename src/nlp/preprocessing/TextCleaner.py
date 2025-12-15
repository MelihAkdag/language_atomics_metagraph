"""Text preprocessing utilities for NLP pipeline."""


class TextCleaner:
    """Handles text cleaning and normalization operations."""
    
    @staticmethod
    def remove_line_breaks(text: str) -> str:
        """Remove line breaks from text.
        
        Args:
            text: Input text with line breaks
            
        Returns:
            Text with line breaks replaced by spaces
        """
        return text.replace('\n', ' ')
    
    @staticmethod
    def remove_multiple_spaces(text: str) -> str:
        """Remove multiple consecutive spaces.
        
        Args:
            text: Input text with multiple spaces
            
        Returns:
            Text with normalized spacing
        """
        return ' '.join(text.split())
    
    @classmethod
    def clean(cls, text: str, coref_resolver=None, coref_strategy: str = 'none', verbose: bool = False) -> str:
        """Apply all cleaning operations to text.
        
        Args:
            text: Raw input text
            coref_resolver: Optional CoreferenceResolver instance
            coref_strategy: Strategy for handling pronouns - 'none', 'filter', or 'replace'
            verbose: Whether to show progress
            
        Returns:
            Cleaned and normalized text
        """
        text = cls.remove_line_breaks(text)
        text = cls.remove_multiple_spaces(text)
        
        # Apply coreference resolution if requested
        if coref_resolver and coref_strategy != 'none':
            text = coref_resolver.resolve_text(text, strategy=coref_strategy, verbose=verbose)
            text = cls.remove_multiple_spaces(text)  # Clean up again after resolution
        
        return text
