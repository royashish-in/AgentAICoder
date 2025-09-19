"""Technology-specific coding agents with best practices."""

from crewai import Agent
from langchain_community.llms import Ollama
from typing import Dict, List
import json
from pathlib import Path

class TechSpecificAgentFactory:
    """Factory for creating technology-specific coding agents."""
    
    def __init__(self):
        from core.llm_config import get_coding_llm
        self.llm = get_coding_llm()
        self.best_practices = self._load_best_practices()
    
    def create_agent(self, tech_stack: List[str]) -> Agent:
        """Create appropriate tech-specific agent based on stack."""
        primary_tech = self._determine_primary_tech(tech_stack)
        
        if primary_tech in ["React", "JavaScript", "TypeScript"]:
            return self._create_react_agent()
        elif primary_tech in ["Python", "Django", "Flask", "FastAPI"]:
            return self._create_python_agent()
        elif primary_tech in ["Java", "Spring"]:
            return self._create_java_agent()
        elif primary_tech in ["C#", ".NET"]:
            return self._create_dotnet_agent()
        else:
            return self._create_generic_agent()
    
    def _create_react_agent(self) -> Agent:
        """Create React/JavaScript specialist agent."""
        return Agent(
            role="React/JavaScript Specialist",
            goal="Generate modern React applications following best practices",
            backstory=f"""You are a React expert with deep knowledge of:
            - Modern React patterns (hooks, context, suspense)
            - TypeScript integration
            - Performance optimization
            - Testing with Jest/RTL
            - Build tools (Vite, Webpack)
            
            Best Practices Library:
            {self.best_practices.get('react', {})}
            
            Always follow these patterns and reuse proven solutions.""",
            llm=self.llm,
            verbose=True
        )
    
    def _create_python_agent(self) -> Agent:
        """Create Python specialist agent."""
        return Agent(
            role="Python/Django Specialist", 
            goal="Generate robust Python applications with proper architecture",
            backstory=f"""You are a Python expert specializing in:
            - Clean architecture patterns
            - Django/FastAPI best practices
            - Async programming
            - Testing with pytest
            - Security patterns
            
            Best Practices Library:
            {self.best_practices.get('python', {})}
            
            Reuse established patterns and maintain consistency.""",
            llm=self.llm,
            verbose=True
        )
    
    def _create_java_agent(self) -> Agent:
        """Create Java/Spring specialist agent."""
        return Agent(
            role="Java/Spring Specialist",
            goal="Generate enterprise-grade Java applications",
            backstory=f"""You are a Java expert with expertise in:
            - Spring Boot ecosystem
            - Microservices patterns
            - JPA/Hibernate optimization
            - Security with Spring Security
            - Testing strategies
            
            Best Practices Library:
            {self.best_practices.get('java', {})}
            
            Follow enterprise patterns and maintain code quality.""",
            llm=self.llm,
            verbose=True
        )
    
    def _create_dotnet_agent(self) -> Agent:
        """Create .NET specialist agent."""
        return Agent(
            role=".NET/C# Specialist",
            goal="Generate scalable .NET applications with modern patterns",
            backstory=f"""You are a .NET expert proficient in:
            - ASP.NET Core patterns
            - Entity Framework optimization
            - Dependency injection
            - Minimal APIs
            - Testing with xUnit
            
            Best Practices Library:
            {self.best_practices.get('dotnet', {})}
            
            Apply modern .NET patterns consistently.""",
            llm=self.llm,
            verbose=True
        )
    
    def _create_generic_agent(self) -> Agent:
        """Fallback generic agent."""
        return Agent(
            role="Full-Stack Developer",
            goal="Generate quality code following general best practices",
            backstory="You are a versatile developer capable of working with various technologies while maintaining code quality standards.",
            llm=self.llm,
            verbose=True
        )
    
    def _determine_primary_tech(self, tech_stack: List[str]) -> str:
        """Determine primary technology from stack."""
        # Priority order for technology selection
        priority_map = {
            "React": 10, "JavaScript": 9, "TypeScript": 8,
            "Python": 10, "Django": 9, "FastAPI": 8, "Flask": 7,
            "Java": 10, "Spring": 9,
            "C#": 10, ".NET": 9, "ASP.NET": 8
        }
        
        best_tech = None
        best_score = 0
        
        for tech in tech_stack:
            score = priority_map.get(tech, 0)
            if score > best_score:
                best_score = score
                best_tech = tech
        
        return best_tech or "Generic"
    
    def _load_best_practices(self) -> Dict:
        """Load technology-specific best practices."""
        return {
            "react": {
                "patterns": [
                    "Use functional components with hooks",
                    "Implement proper error boundaries",
                    "Use React.memo for performance",
                    "Follow component composition patterns",
                    "Implement proper prop validation"
                ],
                "structure": {
                    "components": "src/components/",
                    "hooks": "src/hooks/",
                    "utils": "src/utils/",
                    "types": "src/types/",
                    "tests": "src/__tests__/"
                },
                "dependencies": {
                    "core": ["react", "react-dom"],
                    "testing": ["@testing-library/react", "@testing-library/jest-dom"],
                    "build": ["vite", "@vitejs/plugin-react"]
                }
            },
            "python": {
                "patterns": [
                    "Follow PEP 8 style guidelines",
                    "Use type hints consistently",
                    "Implement proper error handling",
                    "Use dataclasses for data structures",
                    "Follow dependency injection patterns"
                ],
                "structure": {
                    "app": "app/",
                    "models": "app/models/",
                    "views": "app/views/", 
                    "services": "app/services/",
                    "tests": "tests/"
                },
                "dependencies": {
                    "web": ["fastapi", "uvicorn"],
                    "orm": ["sqlalchemy", "alembic"],
                    "testing": ["pytest", "pytest-asyncio"]
                }
            },
            "java": {
                "patterns": [
                    "Use Spring Boot conventions",
                    "Implement proper layered architecture",
                    "Use dependency injection",
                    "Follow REST API standards",
                    "Implement proper exception handling"
                ],
                "structure": {
                    "controller": "src/main/java/controller/",
                    "service": "src/main/java/service/",
                    "repository": "src/main/java/repository/",
                    "model": "src/main/java/model/",
                    "tests": "src/test/java/"
                }
            },
            "dotnet": {
                "patterns": [
                    "Use ASP.NET Core conventions",
                    "Implement clean architecture",
                    "Use dependency injection container",
                    "Follow async/await patterns",
                    "Implement proper validation"
                ],
                "structure": {
                    "controllers": "Controllers/",
                    "services": "Services/",
                    "models": "Models/",
                    "data": "Data/",
                    "tests": "Tests/"
                }
            }
        }

class BestPracticesManager:
    """Manages and evolves coding best practices."""
    
    def __init__(self):
        self.practices_file = Path("coding-crew/data/best_practices.json")
        self.practices = self._load_practices()
    
    def get_practices(self, technology: str) -> Dict:
        """Get best practices for specific technology."""
        return self.practices.get(technology.lower(), {})
    
    def add_practice(self, technology: str, category: str, practice: str):
        """Add new best practice."""
        tech_key = technology.lower()
        if tech_key not in self.practices:
            self.practices[tech_key] = {}
        
        if category not in self.practices[tech_key]:
            self.practices[tech_key][category] = []
        
        if practice not in self.practices[tech_key][category]:
            self.practices[tech_key][category].append(practice)
            self._save_practices()
    
    def update_practice(self, technology: str, old_practice: str, new_practice: str):
        """Update existing practice."""
        tech_key = technology.lower()
        if tech_key in self.practices:
            for category in self.practices[tech_key]:
                if isinstance(self.practices[tech_key][category], list):
                    if old_practice in self.practices[tech_key][category]:
                        idx = self.practices[tech_key][category].index(old_practice)
                        self.practices[tech_key][category][idx] = new_practice
                        self._save_practices()
                        return True
        return False
    
    def _load_practices(self) -> Dict:
        """Load practices from file."""
        if self.practices_file.exists():
            try:
                with open(self.practices_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_practices(self):
        """Save practices to file."""
        self.practices_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.practices_file, 'w') as f:
            json.dump(self.practices, f, indent=2)

class CodeTemplateManager:
    """Manages reusable code templates."""
    
    def __init__(self):
        self.templates_dir = Path("coding-crew/templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def get_template(self, technology: str, template_type: str) -> str:
        """Get code template for specific technology and type."""
        template_file = self.templates_dir / technology / f"{template_type}.template"
        
        if template_file.exists():
            return template_file.read_text()
        
        # Return default template if specific one doesn't exist
        return self._get_default_template(technology, template_type)
    
    def save_template(self, technology: str, template_type: str, content: str):
        """Save code template."""
        tech_dir = self.templates_dir / technology
        tech_dir.mkdir(exist_ok=True)
        
        template_file = tech_dir / f"{template_type}.template"
        template_file.write_text(content)
    
    def _get_default_template(self, technology: str, template_type: str) -> str:
        """Get default template for technology."""
        defaults = {
            "react": {
                "component": """import React from 'react';

interface {{ComponentName}}Props {
  // Define props here
}

const {{ComponentName}}: React.FC<{{ComponentName}}Props> = (props) => {
  return (
    <div>
      {/* Component content */}
    </div>
  );
};

export default {{ComponentName}};""",
                "hook": """import { useState, useEffect } from 'react';

export const use{{HookName}} = () => {
  const [state, setState] = useState();
  
  useEffect(() => {
    // Effect logic
  }, []);
  
  return { state, setState };
};"""
            },
            "python": {
                "service": """from typing import Optional, List
from dataclasses import dataclass

@dataclass
class {{ServiceName}}:
    \"\"\"{{ServiceName}} service class.\"\"\"
    
    def __init__(self):
        pass
    
    async def process(self, data: dict) -> dict:
        \"\"\"Process data and return result.\"\"\"
        # Implementation here
        return {}""",
                "model": """from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class {{ModelName}}(Base):
    __tablename__ = '{{table_name}}'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)"""
            }
        }
        
        return defaults.get(technology, {}).get(template_type, "# Template not found")