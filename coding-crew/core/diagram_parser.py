"""Parse AI-generated text to extract diagram data."""

import re
from typing import Dict, List, Any, Optional


class DiagramParser:
    """Parse AI output to extract structured diagram data."""
    
    def parse_analysis_output(self, text: str) -> Dict[str, Any]:
        """Parse analysis output to extract diagram components."""
        
        # Extract system components
        components = self._extract_components(text)
        
        # Extract component details  
        component_details = self._extract_component_details(text)
        
        # Extract data flow
        data_flow = self._extract_data_flow(text)
        
        return {
            'components': components,
            'component_details': component_details,
            'data_flow': data_flow
        }
    
    def _extract_components(self, text: str) -> List[str]:
        """Extract system components from text."""
        
        # Look for components section
        patterns = [
            r'## System Components\s*```\s*([^`]+)\s*```',
            r'Components:\s*([^\n]+)',
            r'Main components:\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                components_text = match.group(1).strip()
                # Split by comma and clean up
                components = [comp.strip() for comp in components_text.split(',')]
                return [comp for comp in components if comp]
        
        # Fallback: extract from common architecture terms
        fallback_components = []
        architecture_terms = [
            'Frontend', 'Backend', 'Database', 'API Gateway', 
            'User Interface', 'Web Server', 'Application Server',
            'Load Balancer', 'Cache', 'Message Queue'
        ]
        
        for term in architecture_terms:
            if term.lower() in text.lower():
                fallback_components.append(term)
        
        return fallback_components[:4] if fallback_components else ['Frontend', 'Backend', 'Database']
    
    def _extract_component_details(self, text: str) -> Dict[str, List[str]]:
        """Extract detailed component information."""
        
        # Look for component details section
        pattern = r'## Component Details\s*```\s*([^`]+)\s*```'
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        if match:
            details_text = match.group(1).strip()
            return self._parse_component_details_text(details_text)
        
        # Fallback: create basic details
        components = self._extract_components(text)
        return self._generate_default_component_details(components)
    
    def _extract_data_flow(self, text: str) -> List[Dict[str, str]]:
        """Extract data flow steps."""
        
        # Look for data flow section
        patterns = [
            r'## Data Flow Steps\s*```\s*([^`]+)\s*```',
            r'Data Flow:\s*([^\n]+)',
            r'Flow:\s*([^\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                flow_text = match.group(1).strip()
                return self._parse_flow_text(flow_text)
        
        # Fallback: create basic flow
        components = self._extract_components(text)
        return self._generate_default_flow(components)
    
    def _parse_component_details_text(self, text: str) -> Dict[str, List[str]]:
        """Parse component details from structured text."""
        details = {}
        
        # Split by lines and parse each component
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line and '[' in line and ']' in line:
                # Format: "Component: [feature1, feature2, feature3]"
                comp_name = line.split(':')[0].strip()
                features_text = line.split('[')[1].split(']')[0]
                features = [f.strip() for f in features_text.split(',')]
                details[comp_name] = features
        
        return details
    
    def _parse_flow_text(self, text: str) -> List[Dict[str, str]]:
        """Parse flow text into structured steps."""
        steps = []
        
        # Handle arrow-based flow
        if '->' in text:
            parts = text.split('->')
            for i, part in enumerate(parts):
                step_name = part.strip()
                step_type = 'start' if i == 0 else 'end' if i == len(parts) - 1 else 'process'
                steps.append({'name': step_name, 'type': step_type})
        else:
            # Handle line-based flow
            lines = text.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line:
                    step_type = 'start' if i == 0 else 'end' if i == len(lines) - 1 else 'process'
                    steps.append({'name': line, 'type': step_type})
        
        return steps
    
    def _generate_default_component_details(self, components: List[str]) -> Dict[str, List[str]]:
        """Generate default component details."""
        defaults = {
            'Frontend': ['User Interface', 'State Management', 'Routing', 'Authentication UI'],
            'Backend': ['Business Logic', 'API Endpoints', 'Authentication', 'Data Validation'],
            'Database': ['Data Storage', 'Query Processing', 'Indexing', 'Backup'],
            'API Gateway': ['Request Routing', 'Rate Limiting', 'Authentication', 'Load Balancing']
        }
        
        result = {}
        for comp in components:
            result[comp] = defaults.get(comp, ['Core Functionality', 'Data Processing', 'Error Handling'])
        
        return result
    
    def _generate_default_flow(self, components: List[str]) -> List[Dict[str, str]]:
        """Generate default data flow."""
        if len(components) >= 3:
            return [
                {'name': 'User Request', 'type': 'start'},
                {'name': components[0], 'type': 'process'},
                {'name': components[1], 'type': 'process'},
                {'name': components[2], 'type': 'process'},
                {'name': 'Response', 'type': 'end'}
            ]
        else:
            return [
                {'name': 'Input', 'type': 'start'},
                {'name': 'Process', 'type': 'process'},
                {'name': 'Output', 'type': 'end'}
            ]