"""
Google Vertex AI RAG MCP tool.

This tool provides integration with Google Vertex AI's RAG (Retrieval-Augmented Generation)
capabilities for enhanced document search and question answering.

Environment variables:
    GOOGLE_CLOUD_PROJECT: Google Cloud project ID (required)
    GOOGLE_APPLICATION_CREDENTIALS: Path to service account key file (required)
    VERTEX_AI_LOCATION: Vertex AI location/region (default: us-central1)
"""

import os
from typing import Any, Dict, List, Optional
import json

# Conditional imports for Google Cloud dependencies
try:
    from google.cloud import aiplatform
    from google.cloud import discoveryengine_v1beta as discoveryengine
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

from ..core.base import BaseMCPTool


class VertexAIRAGMCPTool(BaseMCPTool):
    """Google Vertex AI RAG tool for document search and Q&A."""

    def __init__(self):
        """Initialize the Vertex AI RAG tool."""
        super().__init__()
        
        if not GOOGLE_CLOUD_AVAILABLE:
            raise ImportError(
                "Google Cloud dependencies not available. Install with: "
                "pip install google-cloud-aiplatform google-cloud-discoveryengine"
            )
        
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
        
        # Initialize Vertex AI
        aiplatform.init(project=self.project_id, location=self.location)
        
        # Initialize Discovery Engine client
        self.discovery_client = discoveryengine.SearchServiceClient()

    def search_documents(
        self,
        query: str,
        search_engine_id: str,
        data_store_id: str,
        num_results: int = 10,
        filter_expression: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search documents using Vertex AI Discovery Engine.

        Args:
            query: Search query string
            search_engine_id: ID of the search engine
            data_store_id: ID of the data store
            num_results: Maximum number of results to return
            filter_expression: Optional filter expression for results

        Returns:
            Dictionary containing search results and metadata
        """
        try:
            # Construct the search request
            search_request = discoveryengine.SearchRequest(
                serving_config=f"projects/{self.project_id}/locations/{self.location}/dataStores/{data_store_id}/servingConfigs/{search_engine_id}",
                query=query,
                page_size=num_results,
                filter=filter_expression,
            )

            # Execute the search
            response = self.discovery_client.search(search_request)

            # Process results
            results = []
            for result in response.results:
                doc_data = result.document.derived_struct_data
                results.append({
                    "title": doc_data.get("title", ""),
                    "content": doc_data.get("content", ""),
                    "url": doc_data.get("link", ""),
                    "score": result.relevance_score,
                    "metadata": dict(doc_data)
                })

            return {
                "results": results,
                "total_count": len(results),
                "query": query,
                "error": None
            }

        except Exception as e:
            return {
                "results": [],
                "total_count": 0,
                "query": query,
                "error": str(e)
            }

    def rag_query(
        self,
        question: str,
        search_engine_id: str,
        data_store_id: str,
        context_documents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform RAG (Retrieval-Augmented Generation) query.

        Args:
            question: Question to answer
            search_engine_id: ID of the search engine
            data_store_id: ID of the data store
            context_documents: Optional list of document IDs to focus on

        Returns:
            Dictionary containing answer and supporting documents
        """
        try:
            # First, search for relevant documents
            search_results = self.search_documents(
                query=question,
                search_engine_id=search_engine_id,
                data_store_id=data_store_id,
                num_results=5
            )

            if search_results["error"]:
                return {
                    "answer": "",
                    "supporting_documents": [],
                    "confidence": 0.0,
                    "error": search_results["error"]
                }

            # Extract context from search results
            context_parts = []
            supporting_docs = []
            
            for result in search_results["results"]:
                context_parts.append(result["content"])
                supporting_docs.append({
                    "title": result["title"],
                    "url": result["url"],
                    "relevance_score": result["score"]
                })

            # Combine context for RAG
            context = "\n\n".join(context_parts)
            
            # Use Vertex AI to generate answer based on retrieved context
            answer_prompt = f"""
            Based on the following context documents, please answer the question: {question}
            
            Context:
            {context}
            
            Please provide a comprehensive answer based on the context. If the context doesn't contain enough information to answer the question, please state that clearly.
            """

            # Initialize Vertex AI model for text generation
            from vertexai.language_models import TextGenerationModel
            
            model = TextGenerationModel.from_pretrained("text-bison@001")
            response = model.predict(
                prompt=answer_prompt,
                max_output_tokens=1024,
                temperature=0.1
            )

            return {
                "answer": response.text,
                "supporting_documents": supporting_docs,
                "confidence": 0.8,  # Placeholder confidence score
                "error": None
            }

        except Exception as e:
            return {
                "answer": "",
                "supporting_documents": [],
                "confidence": 0.0,
                "error": str(e)
            }

    def create_document_index(
        self,
        documents: List[Dict[str, Any]],
        data_store_id: str,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Create or update document index in Vertex AI Discovery Engine.

        Args:
            documents: List of documents to index
            data_store_id: ID of the data store
            batch_size: Number of documents to process in each batch

        Returns:
            Dictionary containing indexing results
        """
        try:
            from google.cloud import discoveryengine_v1beta as discoveryengine
            
            # Initialize document service client
            document_client = discoveryengine.DocumentServiceClient()
            
            indexed_count = 0
            errors = []
            
            # Process documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                for doc in batch:
                    try:
                        # Create document
                        document = discoveryengine.Document(
                            id=doc.get("id", ""),
                            struct_data=doc.get("content", {}),
                            content=discoveryengine.Document.Content(
                                mime_type="application/json",
                                uri=doc.get("uri", "")
                            )
                        )
                        
                        # Create document request
                        request = discoveryengine.CreateDocumentRequest(
                            parent=f"projects/{self.project_id}/locations/{self.location}/dataStores/{data_store_id}/branches/default_branch",
                            document=document
                        )
                        
                        # Create the document
                        response = document_client.create_document(request)
                        indexed_count += 1
                        
                    except Exception as e:
                        errors.append(f"Document {doc.get('id', 'unknown')}: {str(e)}")
            
            return {
                "indexed_count": indexed_count,
                "total_documents": len(documents),
                "errors": errors,
                "success": len(errors) == 0
            }
            
        except Exception as e:
            return {
                "indexed_count": 0,
                "total_documents": len(documents),
                "errors": [str(e)],
                "success": False
            }

    def get_data_stores(self) -> Dict[str, Any]:
        """
        List available data stores in the project.

        Returns:
            Dictionary containing list of data stores
        """
        try:
            from google.cloud import discoveryengine_v1beta as discoveryengine
            
            # Initialize data store service client
            data_store_client = discoveryengine.DataStoreServiceClient()
            
            # List data stores
            parent = f"projects/{self.project_id}/locations/{self.location}"
            request = discoveryengine.ListDataStoresRequest(parent=parent)
            
            response = data_store_client.list_data_stores(request)
            
            data_stores = []
            for data_store in response:
                data_stores.append({
                    "id": data_store.name.split("/")[-1],
                    "name": data_store.display_name,
                    "type": data_store.content_config.name,
                    "state": data_store.state.name
                })
            
            return {
                "data_stores": data_stores,
                "error": None
            }
            
        except Exception as e:
            return {
                "data_stores": [],
                "error": str(e)
            }
