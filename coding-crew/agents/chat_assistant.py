"""
AI Chat Assistant for AgentAI Platform
Provides conversational support for users about projects, requirements, and technical questions.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class ChatAssistant:
    """AI-powered chat assistant for the AgentAI platform."""
    
    def __init__(self):
        self.conversation_history = []
        
    def respond(self, message: str, context: Dict[str, Any], projects: Dict, analyses: Dict) -> str:
        """Generate a response to user message with context awareness."""
        
        # Store message in conversation history
        self.conversation_history.append({
            "role": "user",
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "context": context
        })
        
        # Analyze message intent and generate appropriate response
        response = self._generate_response(message.lower(), context, projects, analyses)
        
        # Store response in conversation history
        self.conversation_history.append({
            "role": "assistant", 
            "message": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _generate_response(self, message: str, context: Dict, projects: Dict, analyses: Dict) -> str:
        """Generate contextual response based on message content and platform state."""
        
        # Project-related queries
        if any(word in message for word in ['project', 'projects']):
            return self._handle_project_queries(message, projects, analyses)
        
        # Technology and stack queries
        elif any(word in message for word in ['tech', 'technology', 'stack', 'framework', 'language']):
            return self._handle_tech_queries(message, analyses)
        
        # Requirements and analysis queries
        elif any(word in message for word in ['requirement', 'requirements', 'analysis', 'analyze']):
            return self._handle_requirements_queries(message, projects, analyses)
        
        # Workflow and process queries
        elif any(word in message for word in ['workflow', 'process', 'phase', 'status']):
            return self._handle_workflow_queries(message, projects)
        
        # Help and guidance queries
        elif any(word in message for word in ['help', 'how', 'what', 'guide', 'tutorial']):
            return self._handle_help_queries(message)
        
        # Greeting and general conversation
        elif any(word in message for word in ['hello', 'hi', 'hey', 'thanks', 'thank you']):
            return self._handle_greetings(message)
        
        # Default response
        else:
            return self._default_response()
    
    def _handle_project_queries(self, message: str, projects: Dict, analyses: Dict) -> str:
        """Handle project-related questions."""
        project_count = len(projects)
        
        if 'how many' in message or 'count' in message:
            if project_count == 0:
                return "You don't have any projects yet. Would you like me to help you create your first project?"
            elif project_count == 1:
                return f"You have 1 project. Would you like me to show you its status or help you create another one?"
            else:
                return f"You have {project_count} projects. I can help you review their status, create new ones, or answer questions about the development process."
        
        elif 'status' in message or 'progress' in message:
            if project_count == 0:
                return "No projects to show status for. Let's create your first project!"
            
            # Get project statuses
            statuses = {}
            for project in projects.values():
                status = project.get('status', 'unknown')
                statuses[status] = statuses.get(status, 0) + 1
            
            status_summary = []
            for status, count in statuses.items():
                status_summary.append(f"{count} {status}")
            
            return f"Project status summary: {', '.join(status_summary)}. Would you like details about any specific project?"
        
        elif 'create' in message or 'new' in message:
            return "I'd be happy to help you create a new project! You can either:\n\n• **Manual Entry**: Define requirements, features, and constraints yourself\n• **JIRA Integration**: Import user stories from your JIRA project\n\nWhich approach would you prefer?"
        
        elif 'latest' in message or 'recent' in message:
            if project_count == 0:
                return "No projects created yet. Ready to start your first one?"
            
            # Get most recent project
            latest_project = max(projects.values(), key=lambda p: p.get('created_at', ''))
            return f"Your most recent project is **{latest_project.get('project_name', 'Unknown')}** (Status: {latest_project.get('status', 'unknown')}). Created on {datetime.fromisoformat(latest_project.get('created_at', '')).strftime('%B %d, %Y')}."
        
        else:
            return f"You have {project_count} project{'s' if project_count != 1 else ''}. I can help you check their status, create new ones, or answer questions about the development workflow."
    
    def _handle_tech_queries(self, message: str, analyses: Dict) -> str:
        """Handle technology stack and framework questions."""
        
        if 'recommend' in message or 'suggest' in message:
            return """I can recommend technology stacks based on your project requirements! Here's what I consider:

**For Web Applications:**
• **Frontend**: React, Angular, Vue.js
• **Backend**: Node.js, Python (FastAPI/Django), Java (Spring)
• **Database**: PostgreSQL, MongoDB, MySQL

**For Mobile Apps:**
• **Cross-platform**: React Native, Flutter
• **Native**: Swift (iOS), Kotlin (Android)

**For APIs:**
• **REST**: FastAPI, Express.js, Spring Boot
• **GraphQL**: Apollo, Hasura

Tell me about your project requirements and I'll provide specific recommendations!"""
        
        elif any(tech in message for tech in ['react', 'angular', 'vue']):
            return """**Frontend Framework Comparison:**

• **React**: Component-based, large ecosystem, flexible
• **Angular**: Full framework, TypeScript-first, enterprise-ready  
• **Vue.js**: Progressive, easy learning curve, great documentation

The choice depends on your team's experience and project complexity. What type of application are you building?"""
        
        elif any(tech in message for tech in ['python', 'node', 'java']):
            return """**Backend Technology Comparison:**

• **Python**: Great for AI/ML, rapid development (FastAPI, Django)
• **Node.js**: JavaScript everywhere, excellent for real-time apps
• **Java**: Enterprise-grade, robust ecosystem (Spring Boot)

Each has strengths for different use cases. What are your project's main requirements?"""
        
        elif 'database' in message or 'db' in message:
            return """**Database Selection Guide:**

• **PostgreSQL**: Robust relational DB, great for complex queries
• **MongoDB**: Document-based, flexible schema, good for rapid development
• **MySQL**: Reliable, widely supported, good for web applications
• **Redis**: In-memory, perfect for caching and sessions

The choice depends on your data structure and scalability needs. What type of data will you be storing?"""
        
        else:
            return "I can help you choose the right technology stack! Tell me about your project requirements - target users, expected scale, and any specific constraints."
    
    def _handle_requirements_queries(self, message: str, projects: Dict, analyses: Dict) -> str:
        """Handle requirements and analysis questions."""
        
        if 'how to' in message or 'define' in message:
            return """**Defining Good Requirements:**

1. **Be Specific**: Clear, measurable objectives
2. **User-Focused**: Define target users and their needs
3. **Functional**: What the system should do
4. **Non-Functional**: Performance, security, scalability needs
5. **Constraints**: Budget, timeline, technology limitations

**Example Structure:**
• Target Users: Who will use this?
• Core Features: What are the main capabilities?
• Scale: How many users/transactions?
• Constraints: Any specific requirements or limitations?

Would you like help structuring requirements for a specific project?"""
        
        elif 'analysis' in message:
            analysis_count = len(analyses)
            if analysis_count == 0:
                return "No analyses have been completed yet. Once you create a project, our AI will analyze the requirements and recommend a technology stack."
            else:
                return f"I've completed {analysis_count} requirement analysis{'es' if analysis_count != 1 else ''}. Each analysis includes technology recommendations, architecture decisions, and timeline estimates. Would you like me to explain any specific analysis?"
        
        elif 'improve' in message or 'better' in message:
            return """**Tips for Better Requirements:**

• **Use User Stories**: "As a [user], I want [goal] so that [benefit]"
• **Include Acceptance Criteria**: Clear definition of "done"
• **Consider Edge Cases**: What could go wrong?
• **Think About Scale**: Current and future needs
• **Security First**: What data needs protection?

Need help refining requirements for a specific project?"""
        
        else:
            return "I can help you define clear, actionable requirements that lead to successful projects. What specific aspect of requirements gathering interests you?"
    
    def _handle_workflow_queries(self, message: str, projects: Dict) -> str:
        """Handle workflow and process questions."""
        
        return """**AgentAI Development Workflow:**

1. **Requirements Analysis** 📋
   • AI analyzes your requirements
   • Recommends technology stack
   • Creates system architecture

2. **Human Approval** ✅
   • Review AI recommendations
   • Request changes if needed
   • Approve to proceed

3. **Development** 💻
   • AI generates code
   • Creates project structure
   • Implements features

4. **Testing** 🧪
   • Automated test generation
   • Issue detection and fixing
   • Quality assurance

5. **Deployment** 🚀
   • Documentation generation
   • Deployment validation
   • Project delivery

Each phase includes human oversight and iterative improvements. Which phase would you like to know more about?"""
    
    def _handle_help_queries(self, message: str) -> str:
        """Handle help and guidance requests."""
        
        if 'start' in message or 'begin' in message:
            return """**Getting Started with AgentAI:**

1. **Create Your First Project**
   • Click "New Project" in the dashboard
   • Choose between manual entry or JIRA import
   • Define your requirements clearly

2. **Review AI Analysis**
   • AI will analyze and recommend tech stack
   • Review recommendations in the Approvals section
   • Approve, request changes, or reject

3. **Monitor Progress**
   • Track development in the Workflows section
   • View generated code and tests
   • Access project files and documentation

Ready to create your first project?"""
        
        elif 'jira' in message:
            return """**JIRA Integration Guide:**

• **Connect**: Import user stories from your JIRA project
• **Select**: Choose relevant stories for development
• **Analyze**: AI processes stories into technical requirements
• **Develop**: Automated code generation based on stories

This approach ensures your development aligns with business requirements. Have you set up JIRA integration?"""
        
        else:
            return """**I can help you with:**

• 🏗️ **Project Creation**: Requirements definition and setup
• 🤖 **AI Analysis**: Understanding technology recommendations  
• 📊 **Workflow Management**: Tracking project progress
• 💻 **Code Review**: Examining generated code and tests
• 🔧 **Technology Choices**: Framework and stack selection
• 📋 **Best Practices**: Requirements and development guidance

What specific area would you like help with?"""
    
    def _handle_greetings(self, message: str) -> str:
        """Handle greetings and social interactions."""
        
        if any(word in message for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your AI development assistant. I can help you create projects, understand technology recommendations, and guide you through the development process. What would you like to work on today?"
        
        elif any(word in message for word in ['thanks', 'thank you']):
            return "You're welcome! I'm here whenever you need help with your projects or have questions about development. Is there anything else I can assist you with?"
        
        else:
            return "I'm here to help with your development projects! Feel free to ask me anything about requirements, technology choices, or the development process."
    
    def _default_response(self) -> str:
        """Default response for unrecognized queries."""
        return """I'm your AI development assistant! I can help you with:

• **Project Management**: Create, track, and manage development projects
• **Requirements Analysis**: Define and refine project requirements  
• **Technology Recommendations**: Choose the right tech stack
• **Code Review**: Understand generated code and architecture
• **Development Guidance**: Best practices and workflow questions

What would you like to know more about?"""
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []