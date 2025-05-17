import os
import traceback
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
            # Open file with binary mode to handle potential encoding issues
            with open(file_path, 'rb') as file:
                try:
                    reader = PdfReader(file)
                    text = ""
                    
                    # Check if PDF is encrypted
                    if reader.is_encrypted:
                        raise ValueError("PDF is encrypted and requires a password to open.")
                    
                    # Extract text from each page
                    for page_num, page in enumerate(reader.pages):
                        try:
                            page_text = page.extract_text() or ""
                            text += page_text + "\n\n"
                        except Exception as page_error:
                            # Log page-specific error but continue with other pages
                            print(f"Warning: Could not extract text from page {page_num+1}: {str(page_error)}")
                    
                    # Return empty string if no text was extracted
                    if not text.strip():
                        return "No extractable text found in PDF."
                    
                    return text.strip()
                except Exception as pdf_error:
                    # Get detailed error information
                    error_details = traceback.format_exc()
                    print(f"PDF parsing error details: {error_details}")
                    
                    # Provide more helpful error message
                    error_msg = str(pdf_error)
                    if "file has not been decrypted" in error_msg.lower():
                        raise ValueError("PDF is encrypted and requires a password to open.")
                    elif "not a pdf" in error_msg.lower() or "EOF marker not found" in error_msg.lower():
                        raise ValueError("The file is not a valid PDF document.")
                    else:
                        raise ValueError(f"Failed to parse PDF: {error_msg}")
            
        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise ValueError(f"Unexpected error processing PDF: {str(e)}")
    
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
            # Open file with binary mode
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                metadata = reader.metadata or {}
                
                # Convert to regular dictionary and clean up
                return {
                    "title": metadata.get("/Title", "") or "",
                    "author": metadata.get("/Author", "") or "",
                    "subject": metadata.get("/Subject", "") or "",
                    "keywords": metadata.get("/Keywords", "") or "",
                    "creator": metadata.get("/Creator", "") or "",
                    "producer": metadata.get("/Producer", "") or "",
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
        errors = []
        
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
                    except (FileNotFoundError, ValueError) as e:
                        # Record errors but continue processing
                        errors.append(f"{file_path}: {str(e)}")
                        continue
        
        # Print summary of errors if any
        if errors:
            print(f"Encountered {len(errors)} errors while processing directory:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"- {error}")
            if len(errors) > 5:
                print(f"... and {len(errors) - 5} more errors")
                        
        return documents