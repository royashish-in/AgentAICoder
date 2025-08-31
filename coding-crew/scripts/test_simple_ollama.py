#!/usr/bin/env python3
"""Simple test of Ollama LLM directly."""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import ChatOllama


def test_direct_ollama():
    """Test Ollama directly without CrewAI."""
    print("🤖 Testing Direct Ollama Connection")
    print("=" * 40)
    
    try:
        # Create Ollama LLM directly
        llm = ChatOllama(
            model="llama3.1:8b",
            base_url="http://localhost:11434",
            temperature=0.1,
        )
        
        print("✅ Created Ollama LLM instance")
        
        # Test simple prompt
        print("🧠 Testing simple prompt...")
        response = llm.invoke("What is a todo application? Answer in 2 sentences.")
        
        print("✅ Got response from Ollama!")
        print(f"📝 Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_direct_ollama()
    
    if success:
        print("\n✅ Direct Ollama test successful!")
        print("🎯 Ollama is working, issue is with CrewAI configuration")
    else:
        print("\n❌ Direct Ollama test failed")
        print("💡 Check if Ollama is running: ollama serve")