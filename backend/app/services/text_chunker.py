from abc import ABC, abstractmethod
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkingStrategy(ABC):
    @abstractmethod
    def chunk_text(self, pages: List[Dict[str, str]]) -> List[Dict[str, any]]:
        pass

class RecursiveCharacterChunker(ChunkingStrategy):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def chunk_text(self, pages: List[Dict[str, str]]) -> List[Dict[str, any]]:
        chunks = []
        chunk_index = 0
        
        for page in pages:
            page_num = page["page"]
            text = page["text"]
            splits = self.splitter.split_text(text)
            
            for split in splits:
                chunks.append({
                    "chunk_index": chunk_index,
                    "text": split,
                    "page_number": page_num,
                    "token_count": len(split) // 4, # rough estimate for MVP
                    # Placeholder for advanced extraction later
                    "heading": None,
                    "section": None,
                    "chapter": None
                })
                chunk_index += 1
                
        return chunks

class TextChunker:
    def __init__(self, strategy: ChunkingStrategy):
        self.strategy = strategy
        
    def process(self, pages: List[Dict[str, str]]) -> List[Dict[str, any]]:
        return self.strategy.chunk_text(pages)
