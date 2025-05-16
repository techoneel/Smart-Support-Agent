import os
from typing import Dict, Any, List
from pypdf import PdfReader

class PDFParser:
    """Parser for extracting text from PDF documents."""
    
    def __init__(self):
        """Initialize the PDF parser."""
        pass
        
    def _create_reader(self, file_path: str) -> PdfReader:
        """Create a PDF reader instance.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            PdfReader: A PdfReader instance
        """
        return PdfReader(file_path)
    
    def extract_text(self, file_path: str) -> str:
        """Extract text content from a PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid PDF
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
            
        try:
            reader = self._create_reader(file_path)
            text = ""
            
            # Extract text from each page
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            
            return text.strip()
            
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from a PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict[str, Any]: Document metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid PDF
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
            
        try:
            reader = self._create_reader(file_path)
            metadata = reader.metadata
            
            # Convert to regular dictionary and clean up
            return {
                "title": metadata.get("/Title", ""),
                "author": metadata.get("/Author", ""),
                "subject": metadata.get("/Subject", ""),
                "keywords": metadata.get("/Keywords", ""),
                "creator": metadata.get("/Creator", ""),
                "producer": metadata.get("/Producer", ""),
                "pages": len(reader.pages)
            }
            
        except Exception as e:
            raise ValueError(f"Failed to extract metadata: {str(e)}")
    
    def process_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Process all PDF files in a directory.
        
        Args:
            directory (str): Directory containing PDF files
            
        Returns:
            List[Dict[str, Any]]: List of documents with text and metadata
            
        Raises:
            NotADirectoryError: If the directory doesn't exist
        """
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Directory not found: {directory}")
            
        documents = []
        
        # Process each PDF file
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    try:
                        text = self.extract_text(file_path)
                        metadata = self.extract_metadata(file_path)
                        
                        documents.append({
                            "file_path": file_path,
                            "text": text,
                            "metadata": metadata
                        })
                    except (FileNotFoundError, ValueError):
                        # Skip files with errors but continue processing
                        continue
                        
        return documents
