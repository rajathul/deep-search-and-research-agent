#!/usr/bin/env python3
"""
Test script for both Deep Search and Deep Research modes
"""

import os
import sys
from planner_agent import PlannerAgent
from planner_agent_deep_research import PlannerAgentDeepResearch

def test_both_modes():
    """Test both research modes with a simple query."""
    print("🧪 Testing Multi-Agent Research System (Both Modes)...")
    
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY='your_api_key_here'")
        return False
    
    try:
        # Initialize both planners
        print("🔧 Initializing Planner Agents...")
        planner_deep_search = PlannerAgent()
        planner_deep_research = PlannerAgentDeepResearch()
        print("✅ Both Planner Agents initialized successfully")
        
        # Test query analysis
        test_question = "What are the recent developments in transformer models?"
        print(f"🔍 Testing query analysis with: '{test_question}'")
        
        # Test Deep Search mode
        print("\n📊 Testing Deep Search Mode:")
        strategy_search = planner_deep_search.analyze_query(test_question)
        print(f"   - Use ArXiv: {strategy_search['use_arxiv']}")
        print(f"   - Use YouTube: {strategy_search['use_youtube']}")
        print(f"   - Complexity: {strategy_search['complexity']}")
        print(f"   - Recency: {strategy_search['recency']}")
        print(f"   - Reasoning: {strategy_search['reasoning']}")
        
        # Test Deep Research mode
        print("\n🔬 Testing Deep Research Mode:")
        strategy_research = planner_deep_research.analyze_query(test_question)
        print(f"   - Use ArXiv: {strategy_research['use_arxiv']}")
        print(f"   - Use YouTube: {strategy_research['use_youtube']}")
        print(f"   - Complexity: {strategy_research['complexity']}")
        print(f"   - Recency: {strategy_research['recency']}")
        print(f"   - Reasoning: {strategy_research['reasoning']}")
        
        # Test decomposition (Deep Research specific)
        print("\n🧩 Testing Question Decomposition:")
        decomposition = planner_deep_research.decomposition_agent.decompose_question(test_question)
        print(f"   - Generated {len(decomposition)} sub-questions:")
        for i, sub_q in enumerate(decomposition, 1):
            print(f"     {i}. {sub_q}")
        
        print("\n✅ System test completed successfully!")
        print("🚀 Your multi-agent system with both modes is ready to use!")
        print("\n💡 Toggle between:")
        print("   - Deep Search: Quick intelligent research")
        print("   - Deep Research: Comprehensive multi-step analysis")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_both_modes()
    sys.exit(0 if success else 1)
