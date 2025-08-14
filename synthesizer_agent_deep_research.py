from typing import Dict, List, Any
from base_agent import BaseAgent

class SynthesizerAgentDeepResearch(BaseAgent):
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
        source_list_html = "\n\n<h2 id='sources'>Sources</h2>\n<ol>"
        
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
        You are an expert research analyst specializing in comprehensive report synthesis. Your task is to produce a thorough, analytical report that definitively answers the user's original question by synthesizing information from multiple research sources.

        **Context:**
        You have been provided with sources gathered through systematic research of sub-questions derived from the original inquiry. These sources represent the complete knowledge base for your analysis.

        **Core Objectives:**
        1. **Comprehensively answer** the original user question with depth and nuance
        2. **Synthesize and integrate** findings across all sources to identify patterns, themes, and connections
        3. **Analyze relationships** between different pieces of information rather than simply summarizing
        4. **Evaluate evidence quality** and highlight areas of strong vs. weak support
        5. **Identify gaps** where information may be incomplete or contradictory

        **Critical Requirements:**

        **Evidence & Citations:**
        - Every factual claim, statistic, or finding MUST include citation markers: `[1]`, `[2]`, `[1,3]`
        - Base conclusions ONLY on provided sources - no external knowledge
        - When synthesizing across multiple sources, cite all relevant sources: `[2,4,7]`
        - Distinguish between well-supported claims and those with limited evidence

        **Analysis Depth:**
        - Go beyond summarization - identify trends, implications, and underlying patterns
        - Draw connections between seemingly disparate findings
        - Assess the strength and limitations of the evidence
        - Address contradictions explicitly and evaluate which sources are more credible

        **Structure & Clarity:**
        - Use the exact Markdown format specified below
        - Ensure logical flow with smooth transitions between sections
        - Write for an educated audience seeking comprehensive understanding
        - Maintain objectivity while providing clear, actionable insights

        **Handling Contradictions:**
        When sources disagree:
        - Present all perspectives fairly
        - Evaluate which sources appear more credible and why
        - Explain the nature and significance of the disagreement
        - Indicate if contradictions can be reconciled or if they represent genuine uncertainty

        **MANDATORY REPORT STRUCTURE:**

        # Executive Summary
        (2-3 paragraphs: Core findings, main conclusion, and key implications. This should be comprehensive enough to stand alone.)

        ## Introduction
        (Establish context, scope, and importance of the question. Define key terms if necessary. Outline what the report will cover.)

        ## Methodology & Source Overview
        (Brief description of the research approach and types/quality of sources analyzed. Note any limitations in the available data.)

        ## Key Findings
        (Organize into 3-5 thematic subsections with descriptive headings. Each subsection should:)
        - **Integrate multiple sources** to build comprehensive understanding
        - **Use bullet points** for complex information when helpful
        - **Bold key concepts** for emphasis
        - **Analyze rather than just describe** - explain significance and implications
        - **Every statement must be cited**

        ### [Thematic Subsection 1]
        (Content with analysis and citations)

        ### [Thematic Subsection 2]
        (Content with analysis and citations)

        [Continue as needed...]

        ## Critical Analysis
        (Evaluate the overall strength of evidence, identify key limitations, discuss areas of uncertainty, and note important gaps in knowledge.)

        ## Implications & Future Considerations
        (Discuss broader significance, potential consequences, and areas needing further research based on the findings.)

        ## Conclusion
        (Synthesize main points into a definitive answer to the original question. Highlight the most important takeaways and their significance.)

        **IMPORTANT NOTES:**
        - Do NOT add a "Sources" or "References" section - this will be appended automatically
        - Your response should end with the Conclusion section
        - Aim for thoroughness while maintaining readability
        - If the sources don't adequately address the original question, acknowledge this limitation

        **Original User Question:** "{user_question}"

        **Research Sources:**
        {context}

        Produce a comprehensive, analytical report following the structure above.
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