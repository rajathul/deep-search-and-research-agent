import json
import re
import os
from google import genai

from tools import tool_query_generator, tool_arxiv_search, tool_synthesis

api_key = os.getenv("GOOGLE_API_KEY")

class Agent:
    def __init__(self, model="gemini-2.0-flash-lite", max_iterations=3):
        """Initialize the agent with configurable model and max iterations."""
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.max_iterations = max_iterations
        self.tools = {
            "query_generator": tool_query_generator,
            "arxiv_search": tool_arxiv_search,
            "synthesis": tool_synthesis
        }
        self.system_prompt = """
        You are a research agent that answers user questions by using tools to query arXiv and synthesize results.
        
        Available Tools:
        - query_generator: Generates an arXiv query string from the user's question. Input: {"user_question": "the question"}. Output: query string.
        - arxiv_search: Searches arXiv using the query and returns a list of papers with titles and summaries. Input: {"query_keywords": "the query", "max_results": 5}. Output: list of paper dicts.
        - synthesis: Synthesizes a sourced answer from the papers. Input: {"original_question": "the question", "papers": [list of paper dicts]}. Output: formatted report.
        
        IMPORTANT: You should complete the entire research process in a single response. Plan your approach:
        1. Generate an arXiv query from the user's question
        2. Search arXiv using that query (use the specified max_results value)
        3. Synthesize the results into a comprehensive answer
        
        Respond ONLY with a single valid JSON object that contains your complete plan:
        {
            "plan": [
                {"tool": "query_generator", "inputs": {"user_question": "..."}},
                {"tool": "arxiv_search", "inputs": {"query_keywords": "...", "max_results": 5}}, 
                {"tool": "synthesis", "inputs": {"original_question": "...", "papers": "PLACEHOLDER"}}
            ]
        }
        
        The agent will execute this plan step by step and use the output of each tool as input to the next.
        Do NOT include any explanations, just the JSON plan.
        """

    def _extract_json(self, text):
        """Extract and parse the first valid JSON object from the text."""
        # Clean code block markers
        text = re.sub(r'^```json\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()

        # Find potential JSON substrings
        matches = re.finditer(r'\{.*\}', text, re.DOTALL)
        for match in matches:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                continue
        return None

    def add_tool(self, name, function):
        """Add a new tool to the agent dynamically."""
        self.tools[name] = function

    def run(self, user_question, date_from=None, date_to=None, max_sources=5):
        """Run the agent to process the user's question."""
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"Agent Iteration {iteration}")
            
            try:
                date_context = ""
                if date_from and date_to:
                    date_context = f'\nIMPORTANT: The user has specified a date range. You MUST include date_from: "{date_from}" and date_to: "{date_to}" in the arxiv_search tool inputs.'
                
                sources_context = f'\nIMPORTANT: The user wants {max_sources} sources. You MUST set max_results: {max_sources} in the arxiv_search tool inputs.'
                
                # Get execution plan from LLM
                plan_prompt = self.system_prompt + f'\n\nUser Question: "{user_question}"' + date_context + sources_context
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=plan_prompt
                )
                
                print(f"Raw Agent Response: {response.text}")
                
                # Parse the plan
                plan_json = self._extract_json(response.text)
                if not plan_json or 'plan' not in plan_json:
                    print("Error: Could not extract valid plan. Retrying...")
                    continue
                
                plan = plan_json['plan']
                print(f"Executing plan with {len(plan)} steps...")
                
                # Execute the plan step by step
                results = {}
                for step_idx, step in enumerate(plan):
                    if 'tool' not in step or 'inputs' not in step:
                        print(f"Error: Invalid step format at step {step_idx}")
                        break
                    
                    tool_name = step['tool']
                    inputs = step['inputs']
                    
                    # Handle placeholder for papers in synthesis step
                    if tool_name == 'synthesis' and inputs.get('papers') == 'PLACEHOLDER':
                        if 'papers' in results:
                            inputs['papers'] = results['papers']
                        else:
                            print("Error: No papers available for synthesis")
                            break
                    
                    # Handle placeholder for query in search step
                    if tool_name == 'arxiv_search' and inputs.get('query_keywords', '').strip() == '':
                        if 'query' in results:
                            inputs['query_keywords'] = results['query']
                        else:
                            print("Error: No query available for search")
                            break
                    
                    if tool_name in self.tools:
                        print(f"Executing step {step_idx + 1}: {tool_name}")

                        if tool_name in ["query_generator", "synthesis"]:
                            result = self.tools[tool_name](self.client, inputs)
                        else:
                            result = self.tools[tool_name](inputs)
                        
                        # Store results for next steps
                        if tool_name == 'query_generator':
                            results['query'] = result
                        elif tool_name == 'arxiv_search':
                            results['papers'] = result
                        elif tool_name == 'synthesis':
                            return result  # Final answer
                    else:
                        print(f"Error: Unknown tool {tool_name}")
                        break
                
            except Exception as e:
                print(f"Agent error in iteration {iteration}: {e}")
                continue
        
        return "Agent failed to complete the task within iterations."
