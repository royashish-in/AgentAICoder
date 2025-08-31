#!/usr/bin/env python3
"""Test CrewAI with direct Ollama configuration."""

import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# Set environment for CrewAI + Ollama
os.environ["OPENAI_API_KEY"] = "sk-fake-key"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"


async def test_direct_crewai():
    """Test CrewAI directly with Ollama."""
    print("🤖 Testing Direct CrewAI + Ollama")
    print("=" * 40)
    
    try:
        # Create Ollama LLM with provider prefix
        llm = ChatOllama(
            model="ollama/llama3.1:8b",
            base_url="http://localhost:11434",
            temperature=0.1,
        )
        
        print("✅ Created Ollama LLM")
        
        # Create simple agent
        analyst = Agent(
            role='System Analyst',
            goal='Analyze requirements and provide recommendations',
            backstory='You are an expert system analyst.',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        print("✅ Created CrewAI Agent")
        
        # Create simple task
        task = Task(
            description="""
            Analyze this requirement: Build a simple todo application with add, complete, and delete features.
            
            Provide:
            1. Brief system overview
            2. Main components needed
            3. Technology recommendations
            
            Keep response under 200 words.
            """,
            agent=analyst,
            expected_output="A brief analysis with system overview, components, and tech stack recommendations."
        )
        
        print("✅ Created Task")
        
        # Create crew
        crew = Crew(
            agents=[analyst],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        print("✅ Created Crew")
        print("🧠 Running CrewAI workflow...")
        
        # Execute crew
        result = crew.kickoff()
        
        print("\n🎉 CrewAI Execution Complete!")
        print("=" * 40)
        print("📊 Result:")
        print(result)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_direct_crewai())
    
    if success:
        print("\n✅ Direct CrewAI test successful!")
        print("🎯 CrewAI + Ollama integration working")
    else:
        print("\n❌ Direct CrewAI test failed")
        print("💡 Need to fix CrewAI configuration")