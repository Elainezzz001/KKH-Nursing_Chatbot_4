import pdfplumber
import json
import os
import re
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import pandas as pd

class PDFProcessor:
    def __init__(self):
        self.model = SentenceTransformer('intfloat/multilingual-e5-large-instruct')
        
    def extract_text_and_tables(self, pdf_path: str) -> Dict[str, List[str]]:
        """Extract text and tables from PDF file"""
        extracted_data = {"text_chunks": [], "table_chunks": []}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text()
                    if text:
                        # Clean and chunk text
                        cleaned_text = self._clean_text(text)
                        chunks = self._chunk_text(cleaned_text)
                        extracted_data["text_chunks"].extend(chunks)
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            table_text = self._table_to_text(table)
                            if table_text.strip():
                                extracted_data["table_chunks"].append(table_text)
                                
        except Exception as e:
            print(f"Error processing PDF: {e}")
            
        return extracted_data
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        return text.strip()
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks
    
    def _table_to_text(self, table: List[List[str]]) -> str:
        """Convert table to readable text"""
        if not table:
            return ""
        
        text_parts = []
        for row in table:
            if row:
                clean_row = [str(cell).strip() if cell else "" for cell in row]
                if any(clean_row):  # Only add non-empty rows
                    text_parts.append(" | ".join(clean_row))
        
        return "\n".join(text_parts)
    
    def create_embeddings(self, chunks: List[str]) -> np.ndarray:
        """Create embeddings for text chunks"""
        if not chunks:
            return np.array([])
        
        embeddings = self.model.encode(chunks, convert_to_tensor=False)
        return embeddings
    
    def save_knowledge_base(self, pdf_path: str, output_path: str = "embedded_knowledge.json"):
        """Process PDF and save embeddings to JSON"""
        print("Extracting text and tables from PDF...")
        extracted_data = self.extract_text_and_tables(pdf_path)
        
        all_chunks = extracted_data["text_chunks"] + extracted_data["table_chunks"]
        
        if not all_chunks:
            print("No content extracted from PDF")
            return
        
        print(f"Creating embeddings for {len(all_chunks)} chunks...")
        embeddings = self.create_embeddings(all_chunks)
        
        knowledge_base = {
            "chunks": all_chunks,
            "embeddings": embeddings.tolist(),
            "metadata": {
                "total_chunks": len(all_chunks),
                "text_chunks": len(extracted_data["text_chunks"]),
                "table_chunks": len(extracted_data["table_chunks"])
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
        
        print(f"Knowledge base saved to {output_path}")
        return knowledge_base
    
    def load_knowledge_base(self, path: str = "embedded_knowledge.json") -> Dict:
        """Load existing knowledge base"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def find_relevant_chunk(self, question: str, knowledge_base: Dict, top_k: int = 1) -> str:
        """Find most relevant chunk for a question"""
        if not knowledge_base or "chunks" not in knowledge_base:
            return "No knowledge base available."
        
        question_embedding = self.model.encode([question])
        stored_embeddings = np.array(knowledge_base["embeddings"])
        
        similarities = cosine_similarity(question_embedding, stored_embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant_chunks = []
        for idx in top_indices:
            relevant_chunks.append(knowledge_base["chunks"][idx])
        
        return "\n\n".join(relevant_chunks)

class QuizGenerator:
    def __init__(self, chunks: List[str]):
        self.chunks = chunks
        self.sentences = self._extract_sentences()
    
    def _extract_sentences(self) -> List[str]:
        """Extract clean sentences from chunks"""
        sentences = []
        for chunk in self.chunks:
            chunk_sentences = chunk.split('. ')
            for sentence in chunk_sentences:
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 20:  # Filter out very short sentences
                    sentences.append(clean_sentence)
        return sentences[:50]  # Limit to 50 sentences for performance
    
    def generate_questions(self, num_questions: int = 15) -> List[Dict]:
        """Generate quiz questions from the content"""
        questions = []
        
        # Simple question generation based on content
        for i, sentence in enumerate(self.sentences[:num_questions]):
            if len(questions) >= num_questions:
                break
                
            # Generate different types of questions
            question_type = i % 3
            
            if question_type == 0:  # True/False
                question = self._generate_true_false(sentence)
            elif question_type == 1:  # Multiple Choice
                question = self._generate_multiple_choice(sentence)
            else:  # Open-ended
                question = self._generate_open_ended(sentence)
            
            if question:
                questions.append(question)
        
        return questions
    
    def _generate_true_false(self, sentence: str) -> Dict:
        """Generate True/False question"""
        return {
            "type": "true_false",
            "question": f"True or False: {sentence}",
            "options": ["True", "False"],
            "answer": "True",  # Assuming the sentence from PDF is true
            "explanation": "This information is directly from the source material."
        }
    
    def _generate_multiple_choice(self, sentence: str) -> Dict:
        """Generate Multiple Choice question"""
        # Extract key terms for the question
        words = sentence.split()
        if len(words) < 5:
            return None
            
        # Simple question generation
        question_text = f"According to the material: {sentence[:50]}..."
        
        return {
            "type": "multiple_choice",
            "question": question_text,
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A",
            "explanation": "Based on the source material."
        }
    
    def _generate_open_ended(self, sentence: str) -> Dict:
        """Generate open-ended question"""
        # Extract key concepts
        question_text = f"Explain the following concept mentioned in the material: {sentence[:30]}..."
        
        return {
            "type": "open_ended",
            "question": question_text,
            "answer": sentence,
            "explanation": "This is based directly on the source material."
        }
