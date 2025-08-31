"""CrewAI workflow orchestrator for the coding crew system."""

from crewai import Crew, Process
from typing import Dict, Any, Optional
from uuid import uuid4
from enum import Enum
from loguru import logger
from pydantic import BaseModel
from core.approval_client import ApprovalClient
from core.diagram_generator import DrawIODiagramGenerator
from core.circuit_breaker import CircuitBreaker

from agents.crew_agents import (
    create_analysis_agent,
    create_architecture_review_agent,
    create_coding_agent,
    create_code_review_agent,
    create_unit_test_agent,
    create_documentation_agent
)
from agents.crew_tasks import (
    create_analysis_task,
    create_architecture_review_task,
    create_coding_task,
    create_code_review_task,
    create_unit_test_task,
    create_documentation_task
)


class WorkflowStage(Enum):
    """Workflow stages."""
    ANALYSIS = "analysis"
    HUMAN_APPROVAL = "human_approval"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    COMPLETED = "completed"


class CrewWorkflowState(BaseModel):
    """Workflow state tracking."""
    workflow_id: str
    correlation_id: str
    stage: WorkflowStage
    requirements: str
    analysis_result: Optional[Dict[str, Any]] = None
    code_result: Optional[Dict[str, Any]] = None
    test_result: Optional[Dict[str, Any]] = None
    documentation_result: Optional[Dict[str, Any]] = None
    approved: bool = False
    completed: bool = False
    error_message: Optional[str] = None
    iteration_count: int = 0
    max_iterations: int = 5


class CrewWorkflowOrchestrator:
    """Orchestrates the CrewAI-based multi-agent workflow."""
    
    def __init__(self):
        self.workflows: Dict[str, CrewWorkflowState] = {}
        self.approval_client = ApprovalClient()
        self.diagram_generator = DrawIODiagramGenerator()
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        
    def create_workflow(self, requirements: str) -> str:
        """Create a new workflow."""
        workflow_id = str(uuid4())
        correlation_id = f"crew_workflow_{workflow_id[:8]}"
        
        state = CrewWorkflowState(
            workflow_id=workflow_id,
            correlation_id=correlation_id,
            stage=WorkflowStage.ANALYSIS,
            requirements=requirements
        )
        
        self.workflows[workflow_id] = state
        
        logger.info(
            f"Created CrewAI workflow {workflow_id}",
            extra={
                "workflow_id": workflow_id,
                "correlation_id": correlation_id,
                "stage": state.stage.value
            }
        )
        
        return workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[CrewWorkflowState]:
        """Get workflow state."""
        return self.workflows.get(workflow_id)
    
    async def run_analysis_phase(self, workflow_id: str) -> Dict[str, Any]:
        """Run the analysis phase with CrewAI."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        logger.info(f"Starting analysis phase for workflow {workflow_id}")
        
        # Create agents and tasks
        analysis_agent = create_analysis_agent()
        review_agent = create_architecture_review_agent()
        
        analysis_task = create_analysis_task(workflow.requirements)
        review_task = create_architecture_review_task()
        
        # Assign agents to tasks
        analysis_task.agent = analysis_agent
        review_task.agent = review_agent
        
        # Set up task dependencies
        review_task.context = [analysis_task]
        
        # Create crew for analysis phase
        analysis_crew = Crew(
            agents=[analysis_agent, review_agent],
            tasks=[analysis_task, review_task],
            process=Process.sequential,
            verbose=True,
            memory=True,
            max_rpm=10  # Rate limiting for Ollama
        )
        
        try:
            # Execute analysis crew
            result = analysis_crew.kickoff()
            
            # Get the analysis text
            analysis_text = result.raw if hasattr(result, 'raw') else str(result)
            
            # Generate system architecture diagram
            try:
                diagram_xml = self.diagram_generator.generate_system_architecture({
                    "components": [
                        {"name": "API Layer", "type": "service"},
                        {"name": "Business Logic", "type": "service"},
                        {"name": "Data Storage", "type": "database"}
                    ]
                })
                diagram_path = self.diagram_generator.save_diagram(diagram_xml, f"architecture_{workflow_id}")
                enhanced_analysis = analysis_text + f"\n\n## System Architecture Diagram\nDiagram saved to: {diagram_path}"
            except Exception as e:
                logger.error(f"Diagram generation failed: {e}")
                enhanced_analysis = analysis_text + "\n\n## System Architecture Diagram\n[Diagram generation failed]"
            
            # Submit for human approval
            analysis_id = self.approval_client.submit_for_approval(
                title=f"System Analysis - {workflow_id[:8]}",
                content=enhanced_analysis,
                diagrams=[]
            )
            
            logger.info(f"Analysis submitted for approval: {analysis_id}")
            
            # Wait for approval
            approval_result = self.approval_client.wait_for_approval(analysis_id)
            
            if not approval_result.get("approved"):
                raise Exception(f"Analysis rejected: {approval_result.get('feedback', 'No feedback')}")
            
            logger.info("Analysis approved, proceeding to development")
            
            # Update workflow state with enhanced analysis
            workflow.analysis_result = {
                "analysis_output": enhanced_analysis,
                "original_output": analysis_text,
                "tasks_output": result.tasks_output if hasattr(result, 'tasks_output') else [],
                "stage_complete": True,
                "diagrams_generated": True,
                "approval": approval_result
            }
            workflow.approved = True
            workflow.stage = WorkflowStage.DEVELOPMENT
            
            logger.info(f"Analysis phase completed for workflow {workflow_id}")
            
            return workflow.analysis_result
            
        except Exception as e:
            logger.error(f"Analysis phase failed for workflow {workflow_id}: {e}")
            raise
    
    async def run_development_phase(self, workflow_id: str) -> Dict[str, Any]:
        """Run the development phase with iterative code generation and review."""
        workflow = self.get_workflow(workflow_id)
        if not workflow or not workflow.approved:
            raise ValueError(f"Workflow {workflow_id} not approved for development")
        
        logger.info(f"Starting development phase for workflow {workflow_id}")
        
        try:
            # Import development workflow
            from core.development_workflow import DevelopmentWorkflow
            
            # Create development workflow with iteration limit
            dev_workflow = DevelopmentWorkflow(max_iterations=5)
            
            # Get analysis result from workflow state
            analysis_output = workflow.analysis_result.get("analysis_output", "")
            
            # Run iterative development cycle with circuit breaker
            development_result = self.circuit_breaker.call(
                dev_workflow.run_development_cycle, analysis_output
            )
            
            # Update workflow state
            workflow.code_result = {
                "code_output": development_result["code"],
                "review_output": development_result["review"],
                "iterations": development_result["iterations"],
                "approved": development_result["approved"],
                "stage_complete": True
            }
            workflow.stage = WorkflowStage.TESTING
            
            logger.info(f"Development phase completed for workflow {workflow_id} after {development_result['iterations']} iterations")
            
            return workflow.code_result
            
        except Exception as e:
            logger.error(f"Development phase failed for workflow {workflow_id}: {e}")
            raise
    
    async def run_testing_phase(self, workflow_id: str) -> Dict[str, Any]:
        """Run the testing phase with comprehensive test generation and execution."""
        workflow = self.get_workflow(workflow_id)
        if not workflow or not workflow.code_result:
            raise ValueError(f"Workflow {workflow_id} not ready for testing")
        
        logger.info(f"Starting testing phase for workflow {workflow_id}")
        
        try:
            # Import testing workflow
            from core.testing_workflow import TestingWorkflow
            
            # Create testing workflow with coverage target
            test_workflow = TestingWorkflow(coverage_target=80.0)
            
            # Get code result from workflow state
            code_output = workflow.code_result.get("code_output", "")
            
            # Run testing cycle with circuit breaker
            testing_result = self.circuit_breaker.call(
                test_workflow.run_testing_cycle, code_output
            )
            
            # Update workflow state
            workflow.test_result = {
                "test_output": testing_result["tests"],
                "execution_output": testing_result["execution"],
                "coverage": testing_result["coverage"],
                "tests_passed": testing_result["tests_passed"],
                "coverage_target_met": testing_result["coverage_target_met"],
                "stage_complete": True
            }
            workflow.stage = WorkflowStage.DOCUMENTATION
            
            logger.info(f"Testing phase completed for workflow {workflow_id} - Coverage: {testing_result['coverage']}%")
            
            return workflow.test_result
            
        except Exception as e:
            logger.error(f"Testing phase failed for workflow {workflow_id}: {e}")
            raise
    
    async def run_documentation_phase(self, workflow_id: str) -> Dict[str, Any]:
        """Run the documentation phase with comprehensive documentation generation."""
        workflow = self.get_workflow(workflow_id)
        if not workflow or not workflow.test_result:
            raise ValueError(f"Workflow {workflow_id} not ready for documentation")
        
        logger.info(f"Starting documentation phase for workflow {workflow_id}")
        
        try:
            # Import documentation workflow
            from core.documentation_workflow import DocumentationWorkflow
            
            # Create documentation workflow
            doc_workflow = DocumentationWorkflow()
            
            # Get results from previous phases
            code_output = workflow.code_result.get("code_output", "")
            test_output = workflow.test_result.get("test_output", "")
            
            # Run documentation cycle with circuit breaker
            doc_result = self.circuit_breaker.call(
                doc_workflow.run_documentation_cycle, code_output, test_output
            )
            
            # Update workflow state
            workflow.documentation_result = {
                "doc_output": doc_result["documentation"],
                "stage_complete": True
            }
            workflow.stage = WorkflowStage.COMPLETED
            workflow.completed = True
            
            logger.info(f"Documentation phase completed for workflow {workflow_id}")
            
            return workflow.documentation_result
            
        except Exception as e:
            logger.error(f"Documentation phase failed for workflow {workflow_id}: {e}")
            raise
    
    def approve_analysis(self, workflow_id: str, approved: bool, feedback: str = "") -> None:
        """Approve or reject analysis phase."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow.approved = approved
        
        if approved:
            workflow.stage = WorkflowStage.DEVELOPMENT
            logger.info(f"Analysis approved for workflow {workflow_id}")
        else:
            workflow.stage = WorkflowStage.ANALYSIS
            logger.info(f"Analysis rejected for workflow {workflow_id}: {feedback}")
    
    def set_workflow_error(self, workflow_id: str, error_message: str) -> None:
        """Set workflow error state."""
        workflow = self.get_workflow(workflow_id)
        if workflow:
            workflow.error_message = error_message
    
    def clear_workflow_error(self, workflow_id: str) -> None:
        """Clear workflow error state."""
        workflow = self.get_workflow(workflow_id)
        if workflow:
            workflow.error_message = None
    
    def reset_workflow(self, workflow_id: str) -> None:
        """Reset workflow to analysis stage."""
        workflow = self.get_workflow(workflow_id)
        if workflow:
            workflow.stage = WorkflowStage.ANALYSIS
            workflow.approved = False
            workflow.completed = False
            workflow.error_message = None
            workflow.iteration_count = 0
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow status."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        return {
            "workflow_id": workflow.workflow_id,
            "stage": workflow.stage.value,
            "approved": workflow.approved,
            "completed": workflow.completed,
            "has_analysis": workflow.analysis_result is not None,
            "has_code": workflow.code_result is not None,
            "has_tests": workflow.test_result is not None,
            "has_documentation": workflow.documentation_result is not None,
            "error_message": workflow.error_message,
            "iteration_count": workflow.iteration_count,
            "max_iterations": workflow.max_iterations
        }