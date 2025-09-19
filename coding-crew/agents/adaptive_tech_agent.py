"""Adaptive agent system for handling new technologies."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
from typing import Dict, List, Optional
import json
import requests
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TechnologyDiscoveryAgent:
    """Agent that discovers and learns new technologies."""
    
    def __init__(self):
        from core.llm_config import get_analysis_llm
        self.llm = get_analysis_llm()
        self.knowledge_base = Path("coding-crew/data/tech_knowledge.json")
        
    def discover_technology(self, tech_name: str) -> Dict:
        """Discover and learn about a new technology."""
        
        # Create discovery agent
        discovery_agent = Agent(
            role="Technology Research Specialist",
            goal=f"Research and understand {tech_name} technology comprehensively",
            backstory=f"""You are an expert technology researcher who quickly learns new 
            programming languages, frameworks, and tools. Your task is to understand 
            {tech_name} and extract key information for code generation.""",
            llm=self.llm,
            verbose=True
        )
        
        # Research task
        research_task = Task(
            description=f"""
            Research {tech_name} technology and provide comprehensive information:
            
            1. TECHNOLOGY OVERVIEW:
               - What is {tech_name}?
               - Primary use cases and applications
               - Key features and capabilities
               
            2. CODING PATTERNS:
               - Common syntax patterns
               - Project structure conventions
               - Naming conventions
               - Best practices
               
            3. ECOSYSTEM:
               - Popular frameworks/libraries
               - Package managers
               - Build tools
               - Testing frameworks
               
            4. DEVELOPMENT WORKFLOW:
               - Project setup process
               - Development commands
               - Build/compilation process
               - Deployment patterns
               
            5. SECURITY CONSIDERATIONS:
               - Common vulnerabilities
               - Security best practices
               - Authentication patterns
               
            6. PERFORMANCE OPTIMIZATION:
               - Common performance issues
               - Optimization techniques
               - Monitoring approaches
               
            Format as structured information that can be used for code generation.
            """,
            agent=discovery_agent,
            expected_output="Comprehensive technology profile with actionable development guidance"
        )
        
        # Execute research
        crew = Crew(
            agents=[discovery_agent],
            tasks=[research_task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Parse and structure the result
        tech_profile = self._parse_research_result(str(result), tech_name)
        
        # Save to knowledge base
        self._save_tech_profile(tech_name, tech_profile)
        
        return tech_profile
    
    def _parse_research_result(self, research_result: str, tech_name: str) -> Dict:
        """Parse research result into structured format."""
        
        # Create parsing agent
        parsing_agent = Agent(
            role="Information Structuring Specialist",
            goal="Convert research text into structured JSON format",
            backstory="You excel at extracting and organizing information into structured formats.",
            llm=self.llm,
            verbose=True
        )
        
        parsing_task = Task(
            description=f"""
            Convert this research about {tech_name} into structured JSON format:
            
            {research_result}
            
            Required JSON structure:
            {{
              "name": "{tech_name}",
              "category": "language|framework|library|tool",
              "patterns": ["pattern1", "pattern2"],
              "structure": {{
                "src": "source directory",
                "tests": "test directory"
              }},
              "dependencies": {{
                "core": ["dep1", "dep2"],
                "dev": ["dev-dep1"]
              }},
              "commands": {{
                "install": "installation command",
                "build": "build command",
                "test": "test command",
                "run": "run command"
              }},
              "file_extensions": [".ext1", ".ext2"],
              "best_practices": ["practice1", "practice2"],
              "security": ["security-tip1", "security-tip2"],
              "performance": ["perf-tip1", "perf-tip2"]
            }}
            
            Extract only factual information from the research.
            """,
            agent=parsing_agent,
            expected_output="Valid JSON structure with technology information"
        )
        
        crew = Crew(
            agents=[parsing_agent],
            tasks=[parsing_task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        try:
            # Extract JSON from result
            import re
            json_match = re.search(r'\{.*\}', str(result), re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"Failed to parse JSON result: {e}")
        
        # Fallback structure
        return {
            "name": tech_name,
            "category": "unknown",
            "patterns": [],
            "structure": {},
            "dependencies": {"core": [], "dev": []},
            "commands": {},
            "file_extensions": [],
            "best_practices": [],
            "security": [],
            "performance": []
        }
    
    def _save_tech_profile(self, tech_name: str, profile: Dict):
        """Save technology profile to knowledge base."""
        
        # Load existing knowledge
        knowledge = {}
        if self.knowledge_base.exists():
            try:
                with open(self.knowledge_base, 'r') as f:
                    knowledge = json.load(f)
            except Exception:
                pass
        
        # Add new technology
        knowledge[tech_name.lower()] = profile
        
        # Save updated knowledge
        self.knowledge_base.parent.mkdir(parents=True, exist_ok=True)
        with open(self.knowledge_base, 'w') as f:
            json.dump(knowledge, f, indent=2)
        
        logger.info(f"Saved technology profile for {tech_name}")

class AdaptiveTechAgentFactory:
    """Factory that creates agents for any technology, including new ones."""
    
    def __init__(self):
        from core.llm_config import get_coding_llm
        self.llm = get_coding_llm()
        self.discovery_agent = TechnologyDiscoveryAgent()
        self.knowledge_base = Path("coding-crew/data/tech_knowledge.json")
    
    def create_agent_for_tech(self, tech_name: str) -> Agent:
        """Create agent for any technology, learning if necessary."""
        
        # Check if we know this technology
        tech_profile = self._get_tech_profile(tech_name)
        
        if not tech_profile:
            logger.info(f"Unknown technology {tech_name}, initiating discovery...")
            tech_profile = self.discovery_agent.discover_technology(tech_name)
        
        # Create specialized agent based on profile
        return self._create_specialized_agent(tech_profile)
    
    def _get_tech_profile(self, tech_name: str) -> Optional[Dict]:
        """Get existing technology profile."""
        if not self.knowledge_base.exists():
            return None
        
        try:
            with open(self.knowledge_base, 'r') as f:
                knowledge = json.load(f)
            return knowledge.get(tech_name.lower())
        except Exception:
            return None
    
    def _create_specialized_agent(self, tech_profile: Dict) -> Agent:
        """Create agent specialized for the technology."""
        
        tech_name = tech_profile.get("name", "Unknown")
        patterns = tech_profile.get("patterns", [])
        best_practices = tech_profile.get("best_practices", [])
        structure = tech_profile.get("structure", {})
        commands = tech_profile.get("commands", {})
        
        return Agent(
            role=f"{tech_name} Specialist Developer",
            goal=f"Generate high-quality {tech_name} code following established patterns",
            backstory=f"""You are a {tech_name} expert with deep knowledge of:
            
            CODING PATTERNS:
            {chr(10).join(f"- {pattern}" for pattern in patterns)}
            
            BEST PRACTICES:
            {chr(10).join(f"- {practice}" for practice in best_practices)}
            
            PROJECT STRUCTURE:
            {chr(10).join(f"- {key}: {value}" for key, value in structure.items())}
            
            DEVELOPMENT COMMANDS:
            {chr(10).join(f"- {key}: {value}" for key, value in commands.items())}
            
            Always follow these established patterns and generate production-ready code.
            """,
            llm=self.llm,
            verbose=True
        )

class BestPracticesEvolution:
    """System that evolves best practices based on successful projects."""
    
    def __init__(self):
        self.practices_file = Path("coding-crew/data/best_practices.json")
        self.success_metrics_file = Path("coding-crew/data/success_metrics.json")
    
    def record_project_success(self, tech_stack: List[str], patterns_used: List[str], 
                             success_metrics: Dict):
        """Record successful project patterns for learning."""
        
        # Load existing metrics
        metrics = self._load_success_metrics()
        
        for tech in tech_stack:
            tech_key = tech.lower()
            
            if tech_key not in metrics:
                metrics[tech_key] = {"successful_patterns": {}, "total_projects": 0}
            
            metrics[tech_key]["total_projects"] += 1
            
            # Track pattern success
            for pattern in patterns_used:
                if pattern not in metrics[tech_key]["successful_patterns"]:
                    metrics[tech_key]["successful_patterns"][pattern] = 0
                metrics[tech_key]["successful_patterns"][pattern] += 1
        
        # Save updated metrics
        self._save_success_metrics(metrics)
        
        # Update best practices based on success rates
        self._update_best_practices(metrics)
    
    def _load_success_metrics(self) -> Dict:
        """Load success metrics."""
        if self.success_metrics_file.exists():
            try:
                with open(self.success_metrics_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_success_metrics(self, metrics: Dict):
        """Save success metrics."""
        self.success_metrics_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.success_metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def _update_best_practices(self, metrics: Dict):
        """Update best practices based on success patterns."""
        
        # Load current practices
        practices = {}
        if self.practices_file.exists():
            try:
                with open(self.practices_file, 'r') as f:
                    practices = json.load(f)
            except Exception:
                pass
        
        # Update practices based on successful patterns
        for tech, tech_metrics in metrics.items():
            if tech not in practices:
                practices[tech] = {"patterns": [], "evolved_practices": []}
            
            # Promote patterns with high success rates
            successful_patterns = tech_metrics.get("successful_patterns", {})
            total_projects = tech_metrics.get("total_projects", 1)
            
            for pattern, success_count in successful_patterns.items():
                success_rate = success_count / total_projects
                
                # If pattern succeeds in >70% of projects, promote to best practice
                if success_rate > 0.7 and pattern not in practices[tech]["patterns"]:
                    practices[tech]["evolved_practices"].append({
                        "pattern": pattern,
                        "success_rate": success_rate,
                        "projects": success_count
                    })
        
        # Save updated practices
        self.practices_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.practices_file, 'w') as f:
            json.dump(practices, f, indent=2)