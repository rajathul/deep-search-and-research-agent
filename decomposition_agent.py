import json
from typing import List, Dict, Any
from base_agent import BaseAgent

class DecompositionAgent(BaseAgent):
    """Agent specialized for breaking down a complex question into sub-questions."""

    def __init__(self):
        super().__init__("Decomposition Agent")

    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """This agent does not search for external sources."""
        return []

    def process_sources(self, sources: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """This agent does not process sources."""
        return sources

    def decompose_question(self, user_question: str) -> List[str]:
        """
        Decomposes the user's main research question into several, more specific
        sub-questions for detailed investigation.
        """
        prompt = f"""
        You are a research strategist. Your task is to break down a complex user question into 3-5 specific, answerable sub-questions that can be used to search academic databases (like ArXiv) and video platforms (like YouTube).

        The sub-questions should cover different facets of the main topic, such as its definition, applications, challenges, and future trends.

        **Main Question:** "{user_question}"

        Return your answer as a JSON object with a single key "sub_questions" containing a list of the generated question strings.

        **Example:**
        Main Question: "What are the latest advancements in using graph neural networks for drug discovery?"
        {{
          "sub_questions": [
            "What are the fundamental principles of graph neural networks?",
            "What are the current applications of GNNs in drug discovery and molecular biology?",
            "What are the recent algorithmic improvements in graph neural networks for scientific research?",
            "What are the challenges and limitations of using GNNs in pharmacology?",
            "What are the future trends and predicted breakthroughs for GNNs in medicine?"
          ]
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            # Clean the response to ensure it's valid JSON
            response_text = response.text.strip() if response.text is not None else ""
            # Find the start and end of the JSON object
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                clean_json_str = response_text[json_start:json_end]
                result = json.loads(clean_json_str)
                return result.get("sub_questions", [user_question])
            else:
                 # Fallback if no JSON is found
                return [user_question]

        except Exception as e:
            print(f"Error during question decomposition: {e}")
            # Fallback to using the original question if decomposition fails
            return [user_question]