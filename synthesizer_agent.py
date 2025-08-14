from typing import Dict, List, Any
from base_agent import BaseAgent

class SynthesizerAgent(BaseAgent):
    """Agent specialized for synthesizing information from multiple sources."""
    
    def __init__(self):
        super().__init__("Synthesizer Agent")
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Synthesizer doesn't search - it processes existing sources."""
        return []
    
    def process_sources(self, sources: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Synthesizer processes sources by creating the final report."""
        return sources
    
    def synthesize(self, user_question: str, all_sources: List[Dict[str, Any]]) -> str:
        """Create a comprehensive report from all sources."""
        if not all_sources:
            return "No relevant sources were found to answer your question."
        
        # Create context for LLM
        context = ""
        source_list_html = "\n\n## Sources\n<ol>"
        
        for i, source in enumerate(all_sources, 1):
            if source.get('source_type') == 'arxiv':
                title = source.get('title', 'No Title')
                info = source.get('summary', '')
                link = source.get('link', '#')
                context += f"Source [{i}]: Title: {title}. Summary: {info}\n\n"
                source_list_html += f'<li id="source-{i}"><a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a></li>'
            
            elif source.get('source_type') == 'youtube':
                title = source.get('title', 'No Title')
                info = source.get('transcript', 'No transcript available.')
                link = source.get('url', '#')
                channel = source.get('channelTitle', '')
                context += f"Source [{i}]: Title: {title}. Channel: {channel}. Transcript: {info}\n\n"
                source_list_html += f'<li id="source-{i}"><a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a> - {channel}</li>'
        
        source_list_html += "</ol>"
        
        # Create synthesis prompt
        prompt = f"""
        You are a meticulous research analyst. Your task is to write a comprehensive, well-structured report that answers the user's question by synthesizing information from the provided sources.

        **Instructions:**
        1. Write a coherent report that integrates the findings from all sources.
        2. For every claim or finding you take from a source, you **must** add a citation marker at the end of the sentence, like `[1]`, `[2]`, or `[1, 3]`.
        3. Base your answer *only* on the information provided in the sources below. Do not use outside knowledge.
        4. Structure your response with clear paragraphs and logical flow.
        5. If sources contradict each other, mention this and present both perspectives.
        6. Do NOT add a "Sources" heading or list. Produce ONLY the report text.

        **Original User Question:** "{user_question}"

        **Sources:**
        {context}

        Produce a comprehensive report text as requested.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model, 
                contents=prompt
            )
            report_text = response.text.strip() if response.text is not None else ""
            return report_text + source_list_html
        except Exception as e:
            return f"Error during synthesis: {e}"