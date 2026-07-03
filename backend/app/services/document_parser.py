from abc import ABC, abstractmethod
import pypdf
from typing import List, Dict

class ExtractionStrategy(ABC):
    @abstractmethod
    def extract_text(self, file_path: str) -> List[Dict[str, str]]:
        pass

class PyPDFExtractionStrategy(ExtractionStrategy):
    def extract_text(self, file_path: str) -> List[Dict[str, str]]:
        pages_content = []
        try:
            with open(file_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        pages_content.append({"page": i + 1, "text": text.strip()})
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
            
        if not pages_content:
            raise ValueError("No extractable text found in PDF.")
            
        return pages_content

class DocumentParser:
    def __init__(self, strategy: ExtractionStrategy):
        self.strategy = strategy
        
    def extract_text(self, file_path: str) -> List[Dict[str, str]]:
        return self.strategy.extract_text(file_path)
