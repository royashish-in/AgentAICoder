"""Enhanced prompts for generating aesthetic diagrams with AI."""


def get_analysis_prompt_with_diagrams(requirements: str) -> str:
    """Get enhanced analysis prompt that generates proper diagram data."""
    return f"""
Analyze the following markdown requirements and create a comprehensive system design:

Requirements:
{requirements}

Your analysis should include:

1. **Parsed and structured requirements**
2. **System architecture recommendations** 
3. **Component breakdown and relationships**
4. **Technology stack suggestions**

5. **IMPORTANT: Provide diagram data in this EXACT format:**

## System Components
```
Frontend, Backend, Database, API Gateway
```

## Component Details
```
Frontend: [User Interface, State Management, Routing, Authentication UI]
Backend: [Business Logic, API Endpoints, Authentication, Data Validation] 
Database: [User Data, Task Storage, Session Management, Audit Logs]
```

## Data Flow Steps
```
User Input -> Frontend -> API Gateway -> Backend -> Database
Database -> Backend -> API Gateway -> Frontend -> User Display
```

Focus on:
- Clear component identification
- Logical data flow
- Professional technology recommendations
- Security and scalability considerations

The diagram data will be used to generate professional draw.io XML diagrams with:
- Consistent color schemes and gradients
- Rounded corners and shadows  
- Clear typography and proper spacing
- Logical flow and organization
"""


def get_review_prompt_with_diagram_feedback() -> str:
    """Get enhanced review prompt that provides diagram improvement feedback."""
    return """
Review the system architecture analysis and provide detailed feedback:

1. **Evaluate the proposed architecture for:**
   - Scalability and performance
   - Security considerations  
   - Maintainability and extensibility
   - Technology stack appropriateness

2. **Review the component structure for:**
   - Component separation and responsibilities
   - Data flow logic and efficiency
   - Missing components or relationships
   - Optimization opportunities

3. **Provide specific recommendations for improvements**

4. **If needed, suggest refined component structure in this format:**

## Refined Components  
```
[Updated component list if changes needed]
```

## Refined Component Details
```
[Updated component details if changes needed]
```

## Refined Data Flow
```
[Updated data flow if changes needed]
```

5. **Ensure the design meets enterprise standards**

Focus on providing actionable feedback that improves:
- System reliability and performance
- Security posture
- Development and maintenance efficiency
- Professional presentation quality
"""