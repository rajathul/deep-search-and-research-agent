import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from google import genai
from ollama import Client as OllamaClient

class BaseAgent(ABC):
    """
    Abstract base class for all research agents.
    Provides common functionality and enforces interface consistency.
    """
    
    def __init__(self, name: str, model: str = "gemma3:4b"):
        self.name = name
        self.model = model
        if "gemini" in self.model.lower():
            self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        else:
            self.client = OllamaClient(
                host='http://localhost:11434'
            )

        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    def update_model(self, model: str):
        """Update the model and reinitialize the client accordingly."""
        self.model = model
        if "gemini" in self.model.lower():
            self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        else:
            self.client = OllamaClient(
                host='http://localhost:11434'
            )
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for relevant sources based on the query."""
        pass
    
    @abstractmethod
    def process_sources(self, sources: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Process and enhance the sources (e.g., fetch transcripts, clean data)."""
        pass
    
    def generate_search_query(self, user_question: str, **kwargs) -> str:
        """Generate optimized search query from user question."""
        prompt = f"""
        Transform the user's question into a concise search query.
        Focus on the most critical technical terms and concepts.
        
        User Question: "{user_question}"
        
        Return ONLY the search query string, no explanations.
        """
        
        try:
            if "gemini" in self.model.lower():
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                return response.text.strip() if response.text is not None else ""
            else:
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt
                )
                return response['response'] if response['response'] is not None else ""

        except Exception as e:
            # Fallback to simple keyword extraction
            import re
            words = re.findall(r"[A-Za-z0-9']+", user_question.lower())
            stopwords = {"the", "a", "an", "of", "in", "on", "for", "and", "to", "with", "is", "are", "how", "what", "why", "who", "where"}
            words = [w for w in words if w not in stopwords and len(w) > 2]
            return " ".join(words[:6])
    
    def run(self, user_question: str, **kwargs) -> Dict[str, Any]:
        """Main execution method for the agent."""
        print(f"{self.name}: Starting research...")
        
        # Generate search query
        query = self.generate_search_query(user_question, **kwargs)
        print(f"{self.name}: Using query: {query}")
        
        # Search for sources
        sources = self.search(query, **kwargs)
        print(f"{self.name}: Found {len(sources)} sources")
        
        # Process sources
        processed_sources = self.process_sources(sources, **kwargs)
        print(f"{self.name}: Processed {len(processed_sources)} sources")
        
        return {
            "agent_name": self.name,
            "query": query,
            "user_question": user_question,
            "sources": processed_sources,
            "source_count": len(processed_sources)
        }