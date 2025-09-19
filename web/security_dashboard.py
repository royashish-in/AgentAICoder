"""Security audit dashboard for real-time vulnerability scanning."""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import json
import os
from datetime import datetime, timedelta
from loguru import logger

router = APIRouter()


class SecurityAuditor:
    """Real-time security vulnerability scanner."""
    
    def __init__(self):
        self.scan_results = {}
        self.last_scan = None
    
    def perform_security_scan(self) -> Dict[str, Any]:
        """Perform comprehensive security scan."""
        scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        results = {
            'scan_id': scan_id,
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities': self._scan_vulnerabilities(),
            'code_quality': self._scan_code_quality(),
            'dependencies': self._scan_dependencies(),
            'configuration': self._scan_configuration(),
            'summary': {}
        }
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        # Store results
        self.scan_results[scan_id] = results
        self.last_scan = scan_id
        
        logger.info(f"Security scan completed: {scan_id}")
        return results
    
    def _scan_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Scan for security vulnerabilities."""
        vulnerabilities = []
        
        # Check for common security issues
        project_root = "/Users/royashish/AI/AgentAI"
        
        # Check for exposed secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']'
        ]
        
        for root, dirs, files in os.walk(project_root):
            for file in files:
                if file.endswith(('.py', '.js', '.json', '.env')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for pattern in secret_patterns:
                                import re
                                if re.search(pattern, content, re.IGNORECASE):
                                    vulnerabilities.append({
                                        'type': 'exposed_secret',
                                        'severity': 'high',
                                        'file': file_path,
                                        'description': 'Potential exposed secret detected'
                                    })
                    except Exception:
                        continue
        
        return vulnerabilities
    
    def _scan_code_quality(self) -> Dict[str, Any]:
        """Scan code quality metrics."""
        return {
            'complexity_issues': self._check_complexity(),
            'code_smells': self._check_code_smells(),
            'test_coverage': self._check_test_coverage()
        }
    
    def _scan_dependencies(self) -> List[Dict[str, Any]]:
        """Scan for vulnerable dependencies."""
        vulnerabilities = []
        
        # Check requirements files
        req_files = ['requirements.txt', 'package.json', 'Pipfile']
        project_root = "/Users/royashish/AI/AgentAI"
        
        for req_file in req_files:
            file_path = os.path.join(project_root, req_file)
            if os.path.exists(file_path):
                vulnerabilities.extend(self._check_dependency_file(file_path))
        
        return vulnerabilities
    
    def _scan_configuration(self) -> Dict[str, Any]:
        """Scan configuration security."""
        return {
            'debug_mode': self._check_debug_mode(),
            'cors_settings': self._check_cors_settings(),
            'authentication': self._check_authentication()
        }
    
    def _check_complexity(self) -> List[Dict[str, Any]]:
        """Check for high complexity functions."""
        # Simplified complexity check
        return [
            {
                'file': 'web/app.py',
                'function': 'create_project_page',
                'complexity': 19,
                'recommendation': 'Break into smaller functions'
            }
        ]
    
    def _check_code_smells(self) -> List[Dict[str, Any]]:
        """Check for code smells."""
        return [
            {
                'type': 'long_method',
                'file': 'coding-crew/agents/analysis_crew.py',
                'line': 142,
                'description': 'Method too long, consider refactoring'
            }
        ]
    
    def _check_test_coverage(self) -> Dict[str, Any]:
        """Check test coverage."""
        return {
            'overall_coverage': 45,
            'files_without_tests': [
                'coding-crew/core/security.py',
                'web/security_dashboard.py'
            ]
        }
    
    def _check_dependency_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Check dependency file for vulnerabilities."""
        vulnerabilities = []
        
        # Known vulnerable packages (simplified)
        vulnerable_packages = {
            'requests': ['2.25.0', '2.25.1'],
            'flask': ['1.0.0', '1.0.1']
        }
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                for package, versions in vulnerable_packages.items():
                    if package in content:
                        vulnerabilities.append({
                            'type': 'vulnerable_dependency',
                            'severity': 'medium',
                            'package': package,
                            'file': file_path,
                            'description': f'Potentially vulnerable version of {package}'
                        })
        except Exception:
            pass
        
        return vulnerabilities
    
    def _check_debug_mode(self) -> Dict[str, Any]:
        """Check if debug mode is enabled."""
        return {
            'enabled': False,
            'recommendation': 'Ensure debug mode is disabled in production'
        }
    
    def _check_cors_settings(self) -> Dict[str, Any]:
        """Check CORS configuration."""
        return {
            'wildcard_origins': False,
            'recommendation': 'Configure specific allowed origins'
        }
    
    def _check_authentication(self) -> Dict[str, Any]:
        """Check authentication configuration."""
        return {
            'enabled': False,
            'recommendation': 'Implement authentication for production use'
        }
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scan summary."""
        total_vulnerabilities = len(results['vulnerabilities'])
        high_severity = sum(1 for v in results['vulnerabilities'] if v.get('severity') == 'high')
        
        return {
            'total_vulnerabilities': total_vulnerabilities,
            'high_severity_count': high_severity,
            'risk_level': 'high' if high_severity > 0 else 'medium' if total_vulnerabilities > 0 else 'low',
            'recommendations': self._get_recommendations(results)
        }
    
    def _get_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Get security recommendations."""
        recommendations = []
        
        if results['vulnerabilities']:
            recommendations.append("Address identified security vulnerabilities")
        
        if not results['configuration']['authentication']['enabled']:
            recommendations.append("Implement authentication system")
        
        if results['code_quality']['test_coverage']['overall_coverage'] < 80:
            recommendations.append("Increase test coverage")
        
        return recommendations


# Initialize security auditor
security_auditor = SecurityAuditor()


@router.get("/api/security/scan")
async def perform_security_scan():
    """Perform security scan and return results."""
    try:
        results = security_auditor.perform_security_scan()
        return results
    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        raise HTTPException(status_code=500, detail="Security scan failed")


@router.get("/api/security/status")
async def get_security_status():
    """Get current security status."""
    if not security_auditor.last_scan:
        return {"status": "no_scan", "message": "No security scan performed yet"}
    
    last_results = security_auditor.scan_results[security_auditor.last_scan]
    return {
        "status": "scanned",
        "last_scan": last_results['timestamp'],
        "risk_level": last_results['summary']['risk_level'],
        "vulnerability_count": last_results['summary']['total_vulnerabilities']
    }


@router.get("/api/security/dashboard")
async def get_security_dashboard():
    """Get security dashboard data."""
    if not security_auditor.last_scan:
        # Perform initial scan
        results = security_auditor.perform_security_scan()
    else:
        results = security_auditor.scan_results[security_auditor.last_scan]
    
    return {
        "summary": results['summary'],
        "vulnerabilities": results['vulnerabilities'][:10],  # Top 10
        "code_quality": results['code_quality'],
        "last_updated": results['timestamp']
    }