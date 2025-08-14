#!/usr/bin/env python3
"""
Test script for the Multi-Agent Research System
"""

import os
import sys
from planner_agent import PlannerAgent

def test_planner_agent():
    """Test the planner agent with a simple query."""
    print("🧪 Testing Multi-Agent Research System...")
    
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY='your_api_key_here'")
        return False
    
    try:
        # Initialize planner agent
        print("🔧 Initializing Planner Agent...")
        planner = PlannerAgent()
        print("✅ Planner Agent initialized successfully")
        
        # Test query analysis
        test_question = "What are the recent developments in transformer models?"
        print(f"🔍 Testing query analysis with: '{test_question}'")
        
        strategy = planner.analyze_query(test_question)
        print("📊 Strategy Analysis:")
        print(f"   - Use ArXiv: {strategy['use_arxiv']}")
        print(f"   - Use YouTube: {strategy['use_youtube']}")
        print(f"   - Complexity: {strategy['complexity']}")
        print(f"   - Recency: {strategy['recency']}")
        print(f"   - Reasoning: {strategy['reasoning']}")
        
        print("\n✅ System test completed successfully!")
        print("🚀 Your multi-agent system is ready to use!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_planner_agent()
    sys.exit(0 if success else 1)
