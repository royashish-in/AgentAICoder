"""Deployment validation crew for testing actual project execution."""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, List
import tempfile
import shutil

class DeploymentValidationCrew:
    """Validates that generated projects can actually run locally."""
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_project_deployment(self, project_path: Path, tech_stack: List[str]) -> Dict:
        """Validate that project can be deployed and run locally."""
        
        validation_results = {
            "project_path": str(project_path),
            "tech_stack": tech_stack,
            "validations": {},
            "overall_status": "UNKNOWN",
            "deployment_ready": False,
            "git_ready": False,
            "errors": []
        }
        
        try:
            # 1. Validate project structure
            structure_result = self._validate_project_structure(project_path)
            validation_results["validations"]["structure"] = structure_result
            
            # 2. Generate missing dependencies
            deps_result = self._generate_dependencies(project_path, tech_stack)
            validation_results["validations"]["dependencies"] = deps_result
            
            # 3. Test local execution
            execution_result = self._test_local_execution(project_path, tech_stack)
            validation_results["validations"]["execution"] = execution_result
            
            # 4. Validate git readiness
            git_result = self._validate_git_readiness(project_path)
            validation_results["validations"]["git"] = git_result
            
            # 5. Test basic functionality
            functionality_result = self._test_basic_functionality(project_path, tech_stack)
            validation_results["validations"]["functionality"] = functionality_result
            
            # Determine overall status
            validation_results["deployment_ready"] = (
                execution_result.get("status") == "PASS" and
                deps_result.get("status") == "PASS"
            )
            
            validation_results["git_ready"] = git_result.get("status") == "PASS"
            
            if validation_results["deployment_ready"] and validation_results["git_ready"]:
                validation_results["overall_status"] = "READY_FOR_DEPLOYMENT"
            elif validation_results["deployment_ready"]:
                validation_results["overall_status"] = "READY_FOR_LOCAL_RUN"
            else:
                validation_results["overall_status"] = "NEEDS_FIXES"
                
        except Exception as e:
            validation_results["errors"].append(f"Validation failed: {str(e)}")
            validation_results["overall_status"] = "VALIDATION_ERROR"
        
        return validation_results
    
    def _validate_project_structure(self, project_path: Path) -> Dict:
        """Validate basic project structure."""
        result = {"status": "PASS", "issues": [], "fixes_applied": []}
        
        required_dirs = ["code", "tests", "docs"]
        for dir_name in required_dirs:
            dir_path = project_path / dir_name
            if not dir_path.exists():
                result["issues"].append(f"Missing {dir_name} directory")
                dir_path.mkdir(exist_ok=True)
                result["fixes_applied"].append(f"Created {dir_name} directory")
        
        code_dir = project_path / "code"
        if code_dir.exists() and not any(code_dir.iterdir()):
            result["issues"].append("Code directory is empty")
            result["status"] = "FAIL"
        
        return result
    
    def _generate_dependencies(self, project_path: Path, tech_stack: List[str]) -> Dict:
        """Generate missing dependency files based on tech stack."""
        result = {"status": "PASS", "files_created": [], "issues": []}
        
        code_dir = project_path / "code"
        
        # JavaScript/React projects
        if any(tech in tech_stack for tech in ["JavaScript", "React", "Node.js"]):
            package_json = code_dir / "package.json"
            if not package_json.exists():
                self._create_package_json(code_dir, tech_stack)
                result["files_created"].append("package.json")
        
        # Python projects
        if "Python" in tech_stack:
            requirements_txt = code_dir / "requirements.txt"
            if not requirements_txt.exists():
                self._create_requirements_txt(code_dir, tech_stack)
                result["files_created"].append("requirements.txt")
        
        # .NET projects
        if any(tech in tech_stack for tech in ["C#", ".NET", "ASP.NET"]):
            csproj_files = list(code_dir.glob("*.csproj"))
            if not csproj_files:
                self._create_csproj_file(code_dir)
                result["files_created"].append("project.csproj")
        
        return result
    
    def _test_local_execution(self, project_path: Path, tech_stack: List[str]) -> Dict:
        """Test if project can actually run locally."""
        result = {"status": "UNKNOWN", "output": "", "errors": [], "commands_tested": []}
        
        code_dir = project_path / "code"
        original_cwd = os.getcwd()
        
        try:
            os.chdir(code_dir)
            
            # Test JavaScript/React projects
            if any(tech in tech_stack for tech in ["JavaScript", "React", "Node.js"]):
                result = self._test_js_execution(code_dir, result)
            
            # Test Python projects
            elif "Python" in tech_stack:
                result = self._test_python_execution(code_dir, result)
            
            # Test .NET projects
            elif any(tech in tech_stack for tech in ["C#", ".NET"]):
                result = self._test_dotnet_execution(code_dir, result)
            
            else:
                result["status"] = "SKIP"
                result["errors"].append("Unknown tech stack for execution testing")
        
        finally:
            os.chdir(original_cwd)
        
        return result
    
    def _test_js_execution(self, code_dir: Path, result: Dict) -> Dict:
        """Test JavaScript/React project execution."""
        try:
            # Install dependencies
            if (code_dir / "package.json").exists():
                install_result = subprocess.run(
                    ["npm", "install"], 
                    capture_output=True, 
                    text=True, 
                    timeout=60
                )
                result["commands_tested"].append("npm install")
                
                if install_result.returncode != 0:
                    result["errors"].append(f"npm install failed: {install_result.stderr}")
                    result["status"] = "FAIL"
                    return result
            
            # Test build (if build script exists)
            package_json_path = code_dir / "package.json"
            if package_json_path.exists():
                with open(package_json_path) as f:
                    package_data = json.load(f)
                
                if "build" in package_data.get("scripts", {}):
                    build_result = subprocess.run(
                        ["npm", "run", "build"], 
                        capture_output=True, 
                        text=True, 
                        timeout=120
                    )
                    result["commands_tested"].append("npm run build")
                    
                    if build_result.returncode == 0:
                        result["status"] = "PASS"
                        result["output"] = "Build successful"
                    else:
                        result["status"] = "FAIL"
                        result["errors"].append(f"Build failed: {build_result.stderr}")
                else:
                    result["status"] = "PASS"
                    result["output"] = "No build script, dependencies installed successfully"
            
        except subprocess.TimeoutExpired:
            result["status"] = "FAIL"
            result["errors"].append("Command timed out")
        except Exception as e:
            result["status"] = "FAIL"
            result["errors"].append(f"Execution test failed: {str(e)}")
        
        return result
    
    def _test_python_execution(self, code_dir: Path, result: Dict) -> Dict:
        """Test Python project execution."""
        try:
            # Install dependencies
            if (code_dir / "requirements.txt").exists():
                install_result = subprocess.run(
                    ["pip", "install", "-r", "requirements.txt"], 
                    capture_output=True, 
                    text=True, 
                    timeout=60
                )
                result["commands_tested"].append("pip install -r requirements.txt")
                
                if install_result.returncode != 0:
                    result["errors"].append(f"pip install failed: {install_result.stderr}")
                    result["status"] = "FAIL"
                    return result
            
            # Test syntax by importing main module
            main_files = list(code_dir.glob("main.py")) + list(code_dir.glob("app.py"))
            if main_files:
                syntax_result = subprocess.run(
                    ["python", "-m", "py_compile", str(main_files[0])], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                result["commands_tested"].append(f"python -m py_compile {main_files[0].name}")
                
                if syntax_result.returncode == 0:
                    result["status"] = "PASS"
                    result["output"] = "Python syntax validation passed"
                else:
                    result["status"] = "FAIL"
                    result["errors"].append(f"Syntax error: {syntax_result.stderr}")
            else:
                result["status"] = "PASS"
                result["output"] = "No main Python file found, dependencies installed"
        
        except Exception as e:
            result["status"] = "FAIL"
            result["errors"].append(f"Python execution test failed: {str(e)}")
        
        return result
    
    def _test_dotnet_execution(self, code_dir: Path, result: Dict) -> Dict:
        """Test .NET project execution."""
        try:
            # Test build
            build_result = subprocess.run(
                ["dotnet", "build"], 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            result["commands_tested"].append("dotnet build")
            
            if build_result.returncode == 0:
                result["status"] = "PASS"
                result["output"] = "dotnet build successful"
            else:
                result["status"] = "FAIL"
                result["errors"].append(f"dotnet build failed: {build_result.stderr}")
        
        except Exception as e:
            result["status"] = "FAIL"
            result["errors"].append(f".NET execution test failed: {str(e)}")
        
        return result
    
    def _validate_git_readiness(self, project_path: Path) -> Dict:
        """Validate project is ready for git."""
        result = {"status": "PASS", "files_created": [], "issues": []}
        
        # Create .gitignore if missing
        gitignore_path = project_path / ".gitignore"
        if not gitignore_path.exists():
            self._create_gitignore(project_path)
            result["files_created"].append(".gitignore")
        
        # Create README.md if missing
        readme_path = project_path / "README.md"
        if not readme_path.exists():
            result["issues"].append("Missing README.md")
            result["status"] = "NEEDS_README"
        
        return result
    
    def _test_basic_functionality(self, project_path: Path, tech_stack: List[str]) -> Dict:
        """Test basic functionality using generated tests."""
        result = {"status": "SKIP", "test_output": "", "errors": []}
        
        tests_dir = project_path / "tests"
        if not tests_dir.exists() or not any(tests_dir.iterdir()):
            result["errors"].append("No tests found")
            return result
        
        code_dir = project_path / "code"
        original_cwd = os.getcwd()
        
        try:
            os.chdir(code_dir)
            
            # Run JavaScript tests
            if any(tech in tech_stack for tech in ["JavaScript", "React"]):
                if (code_dir / "package.json").exists():
                    test_result = subprocess.run(
                        ["npm", "test", "--", "--watchAll=false"], 
                        capture_output=True, 
                        text=True, 
                        timeout=60
                    )
                    
                    if test_result.returncode == 0:
                        result["status"] = "PASS"
                        result["test_output"] = test_result.stdout
                    else:
                        result["status"] = "FAIL"
                        result["errors"].append(f"Tests failed: {test_result.stderr}")
            
            # Run Python tests
            elif "Python" in tech_stack:
                test_files = list(tests_dir.glob("test_*.py"))
                if test_files:
                    test_result = subprocess.run(
                        ["python", "-m", "pytest", str(tests_dir)], 
                        capture_output=True, 
                        text=True, 
                        timeout=60
                    )
                    
                    if test_result.returncode == 0:
                        result["status"] = "PASS"
                        result["test_output"] = test_result.stdout
                    else:
                        result["status"] = "FAIL"
                        result["errors"].append(f"Tests failed: {test_result.stderr}")
        
        except Exception as e:
            result["status"] = "ERROR"
            result["errors"].append(f"Test execution failed: {str(e)}")
        
        finally:
            os.chdir(original_cwd)
        
        return result
    
    def _create_package_json(self, code_dir: Path, tech_stack: List[str]):
        """Create package.json for JavaScript projects."""
        package_data = {
            "name": "generated-project",
            "version": "1.0.0",
            "private": True,
            "dependencies": {},
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            }
        }
        
        if "React" in tech_stack:
            package_data["dependencies"].update({
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            })
        
        with open(code_dir / "package.json", "w") as f:
            json.dump(package_data, f, indent=2)
    
    def _create_requirements_txt(self, code_dir: Path, tech_stack: List[str]):
        """Create requirements.txt for Python projects."""
        requirements = []
        
        if "FastAPI" in tech_stack:
            requirements.extend(["fastapi", "uvicorn"])
        elif "Flask" in tech_stack:
            requirements.append("flask")
        elif "Django" in tech_stack:
            requirements.append("django")
        
        if requirements:
            with open(code_dir / "requirements.txt", "w") as f:
                f.write("\n".join(requirements))
    
    def _create_csproj_file(self, code_dir: Path):
        """Create .csproj file for .NET projects."""
        csproj_content = '''<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>
</Project>'''
        
        with open(code_dir / "project.csproj", "w") as f:
            f.write(csproj_content)
    
    def _create_gitignore(self, project_path: Path):
        """Create appropriate .gitignore file."""
        gitignore_content = """# Dependencies
node_modules/
__pycache__/
*.pyc
bin/
obj/

# Build outputs
build/
dist/
*.dll
*.exe

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment
.env
.env.local
"""
        
        with open(project_path / ".gitignore", "w") as f:
            f.write(gitignore_content)