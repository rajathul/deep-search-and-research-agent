from typing import Dict, List, Any, Optional
from base_agent import BaseAgent
from arxiv_agent import ArxivAgent
from youtube_agent import YoutubeAgent
from synthesizer_agent_deep_research import SynthesizerAgentDeepResearch
from decomposition_agent import DecompositionAgent

class PlannerAgentDeepResearch(BaseAgent):
    """
    Master agent that coordinates other agents and manages the research workflow.
    """
    
    def __init__(self):
        super().__init__("Planner Agent Deep Research")
        self.decomposition_agent = DecompositionAgent()
        self.arxiv_agent = ArxivAgent()
        self.youtube_agent = YoutubeAgent()
        self.synthesizer_agent = SynthesizerAgentDeepResearch()
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Planner doesn't search directly - it coordinates other agents."""
        return []
    
    def process_sources(self, sources: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Planner processes by coordinating synthesis."""
        return sources
    
    def analyze_query(self, user_question: str) -> Dict[str, Any]:
        """Analyze the user query to determine research strategy."""
        prompt = f"""
        Analyze the following research question and determine the best research strategy:

        Question: "{user_question}"

        Consider:
        1. Does this question need academic/scientific papers? (ArXiv useful: yes/no)
        2. Does this question need recent trends/discussions/tutorials? (YouTube useful: yes/no)
        3. What is the complexity level? (simple/medium/complex)
        4. What is the urgency for recent information? (low/medium/high)

        Respond in this exact format:
        ArXiv: yes/no
        YouTube: yes/no
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
                'complexity': 'medium',
                'recency': 'medium',
                'reasoning': 'Default comprehensive research approach'
            }
    
    def execute_research_plan(self, sub_question: str, strategy: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """Execute the research plan based on the strategy."""
        sub_question_sources = []
        max_sources = kwargs.get('max_sources', 10)
        
        # Distribute sources between agents
        if strategy['use_arxiv'] and strategy['use_youtube']:
            arxiv_sources = max(1, max_sources // 2)
            youtube_sources = max(1, max_sources - arxiv_sources)
        elif strategy['use_arxiv']:
            arxiv_sources = max_sources
            youtube_sources = 0
        elif strategy['use_youtube']:
            arxiv_sources = 0
            youtube_sources = max_sources
        else:
            arxiv_sources = max_sources // 2
            youtube_sources = max_sources // 2
        
        print(f"Executing research for sub-question: '{sub_question}'")
        print(f"Research plan: ArXiv={arxiv_sources}, YouTube={youtube_sources}")
        
        # Execute ArXiv research
        if strategy['use_arxiv'] and arxiv_sources > 0:
            try:
                arxiv_result = self.arxiv_agent.run(
                    sub_question,
                    max_results=arxiv_sources,
                    date_from=kwargs.get('date_from'),
                    date_to=kwargs.get('date_to')
                )
                sub_question_sources.extend(arxiv_result.get('sources', []))
            except Exception as e:
                print(f"ArXiv research failed for sub-question '{sub_question}': {e}")
        
        # Execute YouTube research
        if strategy['use_youtube'] and youtube_sources > 0:
            try:
                youtube_result = self.youtube_agent.run(
                    sub_question,
                    max_results=youtube_sources,
                    transcript_limit=kwargs.get('transcript_limit', 3000)
                )
                sub_question_sources.extend(youtube_result.get('sources', []))
            except Exception as e:
                print(f"YouTube research failed for sub-question '{sub_question}': {e}")
        
        # Synthesize results
        # print(f"Synthesizing {len(all_sources)} total sources...")
        # return self.synthesizer_agent.synthesize(user_question, all_sources)
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
        strategy = self.analyze_query(user_question)
        print(f"{self.name}: Using strategy - {strategy['reasoning']}")

        # Step 3: Iterate and execute research for each sub-question
        for i, sub_q in enumerate(sub_questions, 1):
            print(f"\n--- Processing Sub-Question {i}/{len(sub_questions)} ---")
            # We can adjust max_sources per sub-question here if needed
            # For simplicity, we'll use a smaller number per sub-question
            # Example: if total max_sources is 10 and we have 5 sub-questions, use 2 for each.
            #sources_per_sq = max(1, kwargs.get('max_sources', 5) // len(sub_questions))
            sources_per_sq = kwargs.get('max_sources', 5)
            print(f"Allocating {sources_per_sq} sources for this sub-question.")
            
            sub_q_kwargs = kwargs.copy()
            sub_q_kwargs['max_sources'] = sources_per_sq

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