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
    def clean(cls, text: str) -> str:
        """Apply all cleaning operations to text.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned and normalized text
        """
        text = cls.remove_line_breaks(text)
        text = cls.remove_multiple_spaces(text)
        return text
