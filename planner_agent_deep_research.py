from typing import Dict, List, Any, Optional
from base_agent import BaseAgent
from arxiv_agent import ArxivAgent
from youtube_agent import YoutubeAgent
from synthesizer_agent_deep_research import SynthesizerAgentDeepResearch
from decomposition_agent import DecompositionAgent
from webpage_agent import WebpageAgent

class PlannerAgentDeepResearch(BaseAgent):
    """
    Master agent that coordinates other agents and manages the research workflow.
    """
    
    def __init__(self):
        super().__init__("Planner Agent Deep Research")
        self.decomposition_agent = DecompositionAgent()
        self.arxiv_agent = ArxivAgent()
        self.youtube_agent = YoutubeAgent()
        self.webpage_agent = WebpageAgent()
        self.synthesizer_agent = SynthesizerAgentDeepResearch()
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Planner doesn't search directly - it coordinates other agents."""
        return []
    
    def process_sources(self, sources: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Planner processes by coordinating synthesis."""
        return sources
    
    def analyze_query(self, user_question: str, **kwargs) -> Dict[str, Any]:
        """Analyze the user query to determine research strategy."""
        webpage_url = kwargs.get('webpage_url', '')
        
        prompt = f"""
        Analyze the following research question and determine the best research strategy:

        Question: "{user_question}"
        Webpage URL provided: {"Yes" if webpage_url else "No"}

        Consider:
        1. Does this question need academic/scientific papers? (ArXiv useful: yes/no)
        2. Does this question need recent trends/discussions/tutorials? (YouTube useful: yes/no)
        3. Is there a specific webpage to analyze? (Webpage useful: yes/no)
        4. What is the complexity level? (simple/medium/complex)
        5. What is the urgency for recent information? (low/medium/high)

        Respond in this exact format:
        ArXiv: yes/no
        YouTube: yes/no
        Webpage: yes/no
        Complexity: simple/medium/complex
        Recency: low/medium/high
        Reasoning: [brief explanation]
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            analysis_text = response.text.strip() if response.text is not None else ""
            
            # Parse the response
            analysis = {}
            for line in analysis_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    analysis[key.strip().lower()] = value.strip().lower()
            
            return {
                'use_arxiv': analysis.get('arxiv', 'yes') == 'yes',
                'use_youtube': analysis.get('youtube', 'yes') == 'yes',
                'use_webpage': analysis.get('webpage', 'yes') == 'yes' and bool(webpage_url),
                'complexity': analysis.get('complexity', 'medium'),
                'recency': analysis.get('recency', 'medium'),
                'reasoning': analysis.get('reasoning', 'Standard research approach')
            }
        except Exception as e:
            print(f"Query analysis failed: {e}")
            # Default strategy
            return {
                'use_arxiv': True,
                'use_youtube': True,
                'use_webpage': bool(webpage_url),
                'complexity': 'medium',
                'recency': 'medium',
                'reasoning': 'Default comprehensive research approach'
            }
    
    def execute_research_plan(self, sub_question: str, strategy: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """Execute the research plan based on the strategy."""
        sub_question_sources = []
        max_sources = kwargs.get('max_sources', 10)
        webpage_url = kwargs.get('webpage_url', '')
        
        # Calculate source distribution
        active_agents = sum([strategy['use_arxiv'], strategy['use_youtube'], strategy['use_webpage']])
        if active_agents == 0:
            active_agents = 2  # Default to ArXiv and YouTube
            strategy['use_arxiv'] = True
            strategy['use_youtube'] = True
        
        sources_per_agent = max(1, max_sources // active_agents)
        
        print(f"Executing research for sub-question: '{sub_question}'")
        print(f"Research plan: ArXiv={strategy['use_arxiv']}, YouTube={strategy['use_youtube']}, Webpage={strategy['use_webpage']}")
        
        # Execute ArXiv research
        if strategy['use_arxiv']:
            try:
                arxiv_result = self.arxiv_agent.run(
                    sub_question,
                    max_results=sources_per_agent,
                    date_from=kwargs.get('date_from'),
                    date_to=kwargs.get('date_to')
                )
                sub_question_sources.extend(arxiv_result.get('sources', []))
            except Exception as e:
                print(f"ArXiv research failed for sub-question '{sub_question}': {e}")
        
        # Execute YouTube research
        if strategy['use_youtube']:
            try:
                youtube_result = self.youtube_agent.run(
                    sub_question,
                    max_results=sources_per_agent,
                    transcript_limit=kwargs.get('transcript_limit', 3000)
                )
                sub_question_sources.extend(youtube_result.get('sources', []))
            except Exception as e:
                print(f"YouTube research failed for sub-question '{sub_question}': {e}")
        
        # Execute Webpage research (only for the first sub-question to avoid duplication)
        if strategy['use_webpage'] and webpage_url and sub_question == kwargs.get('first_sub_question'):
            try:
                webpage_result = self.webpage_agent.run(
                    sub_question,
                    url=webpage_url
                )
                sub_question_sources.extend(webpage_result.get('sources', []))
            except Exception as e:
                print(f"Webpage research failed for sub-question '{sub_question}': {e}")
        
        return sub_question_sources
    
    def run(self, user_question: str, **kwargs) -> Dict[str, Any]:
        """
        Main execution method that coordinates the entire DEEP research process.
        """
        print(f"{self.name}: Starting comprehensive research for: '{user_question}'")
        all_sources = []
        
        # Step 1: Decompose the main question
        print(f"{self.name}: Decomposing main question...")
        sub_questions = self.decomposition_agent.decompose_question(user_question)
        print(f"{self.name}: Generated {len(sub_questions)} sub-questions.")

        # Step 2: Analyze the query to create a general strategy
        strategy = self.analyze_query(user_question, **kwargs)
        print(f"{self.name}: Using strategy - {strategy['reasoning']}")

        # Step 3: Iterate and execute research for each sub-question
        for i, sub_q in enumerate(sub_questions, 1):
            print(f"\n--- Processing Sub-Question {i}/{len(sub_questions)} ---")
            sources_per_sq = kwargs.get('max_sources', 5)
            print(f"Allocating {sources_per_sq} sources for this sub-question.")
            
            sub_q_kwargs = kwargs.copy()
            sub_q_kwargs['max_sources'] = sources_per_sq
            # Mark the first sub-question for webpage processing
            if i == 1:
                sub_q_kwargs['first_sub_question'] = sub_q

            # Execute the plan for the sub-question
            sources_for_sub_q = self.execute_research_plan(sub_q, strategy, **sub_q_kwargs)
            all_sources.extend(sources_for_sub_q)
        
        print(f"\n--- Synthesis Stage ---")
        print(f"{self.name}: Aggregated {len(all_sources)} sources from all sub-questions.")

        # Step 4: Synthesize the final report from all collected sources
        final_report = self.synthesizer_agent.synthesize(user_question, all_sources)
        
        print(f"{self.name}: Research complete!")
        return {
            "result": final_report,
            "strategy": strategy,
            "sub_questions": sub_questions,
            "agent": self.name
        }