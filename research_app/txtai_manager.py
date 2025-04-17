# txtai Manager
# Handles indexing, retrieval, and metadata management.

import os
import json
from txtai.embeddings import Embeddings
import logging

logger = logging.getLogger(__name__)

class TxtaiManager:
    def __init__(self, index_path="/app/txtai_index/research_index"):
        self.index_path = index_path
        self.embeddings = None
        self._initialize_embeddings()

    def _initialize_embeddings(self):
        """
        Initialize txtai embeddings with appropriate settings for hardware constraints
        """
        # Configure embeddings with all-MiniLM-L6-v2 model (efficient for the hardware)
        self.embeddings = Embeddings(
            {
                "path": "sentence-transformers/all-MiniLM-L6-v2",
                "content": True,  # Store content in the index
                "faiss": {
                    "nprobe": 6,  # Number of clusters to search (performance vs accuracy tradeoff)
                    "components": ["Flat"]  # Use flat index for better accuracy on smaller datasets
                }
            }
        )

        # Load existing index if available
        if os.path.exists(f"{self.index_path}.tar.gz"):
            try:
                logger.info(f"Loading existing index from {self.index_path}.tar.gz")
                self.embeddings.load(self.index_path)
            except Exception as e:
                logger.error(f"Error loading index: {str(e)}")
                # Continue with a fresh index
                pass

    def index_documents(self, documents):
        """
        Index cleaned and chunked documents

        Args:
            documents: List of document dictionaries with text and metadata

        Returns:
            Number of documents indexed
        """
        if not documents:
            return 0

        # Prepare data for indexing
        data = []
        for idx, doc in enumerate(documents):
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})

            # Store full document content and metadata
            data.append((idx, text, metadata))

        # Index the documents
        self.embeddings.index(data)

        # Save the index to disk
        self._save_index()

        return len(documents)

    def retrieve(self, query, limit=10):
        """
        Retrieve relevant content for a query

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of retrieved documents with text and metadata
        """
        if not self.embeddings:
            logger.error("Embeddings not initialized")
            return []

        try:
            # Retrieve results
            results = self.embeddings.search(query, limit)

            retrieved_docs = []
            for result in results:
                # Extract the stored metadata
                if isinstance(result, dict):
                    # Format may vary depending on txtai version
                    text = result.get("text", "")
                    metadata = result.get("metadata", {})
                    score = result.get("score", 0)
                elif isinstance(result, tuple) and len(result) >= 2:
                    # Handle tuple format (text, score)
                    text = result[0]
                    score = result[1]
                    metadata = {}
                else:
                    # Skip invalid results
                    continue

                retrieved_docs.append({
                    "text": text,
                    "metadata": metadata,
                    "score": score
                })

            return retrieved_docs
        except Exception as e:
            logger.error(f"Error retrieving results: {str(e)}")
            return []

    def _save_index(self):
        """
        Save the index to disk
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

            # Save the index
            self.embeddings.save(self.index_path)
            logger.info(f"Index saved to {self.index_path}")
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")

    def get_index_info(self):
        """
        Return information about the current index
        """
        try:
            index_exists = os.path.exists(f"{self.index_path}.tar.gz")
            document_count = len(self.embeddings.search("", 1)) if self.embeddings else 0

            return {
                "index_exists": index_exists,
                "document_count": document_count,
                "index_path": self.index_path,
                "model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        except Exception as e:
            logger.error(f"Error getting index info: {str(e)}")
            return {
                "index_exists": False,
                "error": str(e)
            }
