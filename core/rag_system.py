"""
AgriSense AI - RAG (Retrieval Augmented Generation) System
Advanced document processing and knowledge retrieval for agricultural content
"""

import os
import uuid
import hashlib
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import PyPDF2
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
import openai

class RAGSystem:
    """Advanced RAG system for agricultural document processing"""
    
    def __init__(self, vectordb_path: str):
        self.vectordb_path = vectordb_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=vectordb_path)
        self.collection = self._get_or_create_collection()
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        ) if os.getenv('OPENAI_API_KEY') else None
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Agricultural keywords for relevance scoring
        self.agricultural_keywords = [
            'farming', 'agriculture', 'crop', 'harvest', 'planting', 'soil', 'fertilizer',
            'irrigation', 'pest', 'disease', 'livestock', 'cattle', 'poultry', 'fish',
            'rice', 'maize', 'cassava', 'yam', 'tomato', 'pepper', 'beans', 'groundnut',
            'weather', 'climate', 'season', 'rainfall', 'drought', 'flood',
            'market', 'price', 'cooperative', 'extension', 'training', 'technology',
            'organic', 'sustainable', 'productivity', 'yield', 'storage', 'processing'
        ]
    
    def _get_or_create_collection(self):
        """Get or create ChromaDB collection for agricultural documents"""
        try:
            collection = self.chroma_client.get_collection("agrisense_documents")
            self.logger.info("Retrieved existing ChromaDB collection")
        except:
            collection = self.chroma_client.create_collection(
                name="agrisense_documents",
                metadata={"description": "Agricultural documents and knowledge base"}
            )
            self.logger.info("Created new ChromaDB collection")
        
        return collection
    
    def process_document(self, file, user_id: int) -> str:
        """Process uploaded PDF document and add to vector database"""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            
            # Save file temporarily
            temp_path = os.path.join("/tmp", unique_filename)
            file.save(temp_path)
            
            # Extract text from PDF
            text_content = self._extract_pdf_text(temp_path)
            
            if not text_content:
                raise ValueError("No text content extracted from PDF")
            
            # Check if document is agricultural
            agricultural_score = self._calculate_agricultural_relevance(text_content)
            if agricultural_score < 0.1:
                self.logger.warning(f"Document {file.filename} has low agricultural relevance score: {agricultural_score}")
            
            # Split text into chunks
            documents = self._split_text_into_chunks(text_content, file.filename, user_id)
            
            # Generate embeddings and store
            self._store_documents(documents, unique_filename)
            
            # Clean up temporary file
            os.remove(temp_path)
            
            self.logger.info(f"Successfully processed document: {file.filename} -> {unique_filename}")
            return unique_filename
            
        except Exception as e:
            self.logger.error(f"Error processing document {file.filename}: {str(e)}")
            raise
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\\n--- Page {page_num + 1} ---\\n{page_text}\\n"
                    except Exception as e:
                        self.logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                        continue
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error reading PDF file {file_path}: {str(e)}")
            raise
    
    def _calculate_agricultural_relevance(self, text: str) -> float:
        """Calculate relevance score for agricultural content"""
        text_lower = text.lower()
        keyword_count = 0
        total_words = len(text.split())
        
        for keyword in self.agricultural_keywords:
            keyword_count += text_lower.count(keyword)
        
        if total_words == 0:
            return 0.0
        
        # Calculate relevance score as keyword density
        relevance_score = min(keyword_count / (total_words * 0.1), 1.0)
        return relevance_score
    
    def _split_text_into_chunks(self, text: str, filename: str, user_id: int) -> List[Document]:
        """Split text into overlapping chunks for better retrieval"""
        chunks = self.text_splitter.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    'source': filename,
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'agricultural_score': self._calculate_agricultural_relevance(chunk)
                }
            )
            documents.append(doc)
        
        return documents
    
    def _store_documents(self, documents: List[Document], filename: str):
        """Store documents in vector database"""
        if not self.embeddings:
            raise ValueError("OpenAI embeddings not available")
        
        try:
            # Prepare data for ChromaDB
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            ids = [f"{filename}_{i}" for i in range(len(documents))]
            
            # Generate embeddings
            embeddings = self.embeddings.embed_documents(texts)
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.info(f"Stored {len(documents)} document chunks in vector database")
            
        except Exception as e:
            self.logger.error(f"Error storing documents in vector database: {str(e)}")
            raise
    
    def search(self, query: str, k: int = 5, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for relevant documents using semantic similarity"""
        try:
            if not self.embeddings:
                return []
            
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Prepare where clause for user filtering
            where_clause = None
            if user_id:
                where_clause = {"user_id": user_id}
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k * 2,  # Get more results to filter
                where=where_clause
            )
            
            if not results['documents'][0]:
                return []
            
            # Process and rank results
            processed_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                # Calculate relevance score
                relevance_score = max(0, 1 - distance)  # Convert distance to similarity
                agricultural_score = metadata.get('agricultural_score', 0.5)
                
                # Combined score
                combined_score = (relevance_score * 0.7) + (agricultural_score * 0.3)
                
                processed_results.append({
                    'content': doc,
                    'metadata': metadata,
                    'relevance_score': relevance_score,
                    'agricultural_score': agricultural_score,
                    'combined_score': combined_score,
                    'source': metadata.get('source', 'Unknown'),
                    'chunk_id': metadata.get('chunk_id', 0)
                })
            
            # Sort by combined score and return top k
            processed_results.sort(key=lambda x: x['combined_score'], reverse=True)
            return processed_results[:k]
            
        except Exception as e:
            self.logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def get_document_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get statistics about stored documents"""
        try:
            # Get all documents
            results = self.collection.get()
            
            if not results['metadatas']:
                return {
                    'total_documents': 0,
                    'total_chunks': 0,
                    'user_documents': 0 if user_id else None
                }
            
            total_chunks = len(results['metadatas'])
            unique_sources = set()
            user_chunks = 0
            
            for metadata in results['metadatas']:
                unique_sources.add(metadata.get('source', 'Unknown'))
                if user_id and metadata.get('user_id') == user_id:
                    user_chunks += 1
            
            return {
                'total_documents': len(unique_sources),
                'total_chunks': total_chunks,
                'user_documents': user_chunks if user_id else None,
                'average_chunks_per_document': total_chunks / len(unique_sources) if unique_sources else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting document stats: {str(e)}")
            return {'error': str(e)}
    
    def delete_document(self, filename: str, user_id: Optional[int] = None) -> bool:
        """Delete a document and all its chunks"""
        try:
            # Get document IDs to delete
            results = self.collection.get()
            ids_to_delete = []
            
            for i, metadata in enumerate(results['metadatas']):
                if metadata.get('source') == filename:
                    # Check user permission if user_id provided
                    if user_id and metadata.get('user_id') != user_id:
                        continue
                    ids_to_delete.append(results['ids'][i])
            
            if not ids_to_delete:
                return False
            
            # Delete from ChromaDB
            self.collection.delete(ids=ids_to_delete)
            
            self.logger.info(f"Deleted {len(ids_to_delete)} chunks for document {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting document {filename}: {str(e)}")
            return False
    
    def get_similar_content(self, content: str, k: int = 3) -> List[Dict[str, Any]]:
        """Find similar content to given text"""
        return self.search(content, k=k)
    
    def update_agricultural_keywords(self, new_keywords: List[str]):
        """Update the list of agricultural keywords for relevance scoring"""
        self.agricultural_keywords.extend(new_keywords)
        self.agricultural_keywords = list(set(self.agricultural_keywords))  # Remove duplicates
        self.logger.info(f"Updated agricultural keywords. Total: {len(self.agricultural_keywords)}")
    
    def get_keyword_suggestions(self, text: str) -> List[str]:
        """Extract potential agricultural keywords from text"""
        words = text.lower().split()
        word_freq = {}
        
        for word in words:
            # Clean word
            clean_word = ''.join(char for char in word if char.isalnum())
            if len(clean_word) > 3:  # Only consider words longer than 3 characters
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Sort by frequency and return top suggestions
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        suggestions = [word for word, freq in sorted_words[:10] if word not in self.agricultural_keywords]
        
        return suggestions