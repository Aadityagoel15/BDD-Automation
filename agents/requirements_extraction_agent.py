"""
Requirements Extraction Agent
Extracts testing requirements from project files, code, documentation, etc.
"""
import os
import re
from pathlib import Path
from groq_client import GroqClient
from config import Config

class RequirementsExtractionAgent:
    """Agent that extracts requirements from projects for BDD testing"""
    
    def __init__(self):
        self.groq_client = GroqClient()
        self.system_prompt = """You are an expert in software testing and requirements analysis.
Your task is to analyze project files, code, documentation, or user stories and extract testable requirements.

Guidelines:
1. Extract user stories or functional requirements
2. Identify testable features and functionalities
3. Convert technical details into user-focused requirements
4. Format as clear, testable user stories following BDD format
5. Include acceptance criteria when available
6. Be comprehensive but organized
7. Group related requirements together
8. Focus on what can be tested, not implementation details
"""
    
    def extract_from_code(self, code_content: str, file_path: str = None) -> str:
        """
        Extract requirements from source code
        
        Args:
            code_content: Source code content
            file_path: Optional file path for context
            
        Returns:
            Extracted requirements as text
        """
        file_type = "unknown"
        if file_path:
            file_type = Path(file_path).suffix
        
        prompt = f"""Analyze the following source code and extract testable requirements:

FILE TYPE: {file_type}
CODE:
{code_content[:5000]}  # Limit to first 5000 chars

Extract:
1. Main functionalities
2. User-facing features
3. Business logic that needs testing
4. Edge cases or error handling
5. Input validation requirements

Format as clear user stories or requirements suitable for BDD testing."""
        
        try:
            requirements = self.groq_client.generate_response(prompt, self.system_prompt)
            return requirements
        except Exception as e:
            return f"Error extracting requirements from code: {str(e)}"
    
    def extract_from_documentation(self, doc_content: str, doc_type: str = "README") -> str:
        """
        Extract requirements from documentation files
        
        Args:
            doc_content: Documentation content
            doc_type: Type of documentation (README, API docs, etc.)
            
        Returns:
            Extracted requirements as text
        """
        prompt = f"""Analyze the following {doc_type} documentation and extract testable requirements:

DOCUMENTATION:
{doc_content[:5000]}  # Limit to first 5000 chars

Extract:
1. Features described
2. User stories mentioned
3. Functional requirements
4. Acceptance criteria
5. Use cases

Format as clear, testable user stories suitable for BDD testing."""
        
        try:
            requirements = self.groq_client.generate_response(prompt, self.system_prompt)
            return requirements
        except Exception as e:
            return f"Error extracting requirements from documentation: {str(e)}"
    
    def extract_from_user_stories(self, user_stories: str) -> str:
        """
        Extract and format requirements from user stories text
        
        Args:
            user_stories: User stories text
            
        Returns:
            Formatted requirements
        """
        prompt = f"""Analyze the following user stories and extract/format them as testable requirements:

USER STORIES:
{user_stories}

Extract and format:
1. Clear user stories following the pattern: "As a [user], I want [action] so that [benefit]"
2. Acceptance criteria
3. Edge cases
4. Test scenarios

Ensure all requirements are testable and suitable for BDD feature files."""
        
        try:
            requirements = self.groq_client.generate_response(prompt, self.system_prompt)
            return requirements
        except Exception as e:
            return f"Error processing user stories: {str(e)}"
    
    def extract_from_project_directory(self, project_path: str, file_extensions: list = None) -> dict:
        """
        Extract requirements from all relevant files in a project directory
        
        Args:
            project_path: Path to project directory
            file_extensions: List of file extensions to analyze (e.g., ['.py', '.js', '.md'])
            
        Returns:
            Dictionary with extracted requirements organized by file/type
        """
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.java', '.md', '.txt', '.yaml', '.yml', '.json']
        
        project_path = Path(project_path)
        if not project_path.exists():
            return {"error": f"Project path does not exist: {project_path}"}
        
        extracted_requirements = {
            "project_path": str(project_path),
            "requirements_by_file": {},
            "combined_requirements": ""
        }
        
        # Common ignore patterns
        ignore_patterns = [
            '__pycache__', '.git', 'node_modules', 'venv', 'env', 
            '.pytest_cache', 'coverage', 'dist', 'build', '.idea', '.vscode'
        ]
        
        requirements_parts = []
        
        # Scan for documentation files first
        doc_files = []
        for ext in ['.md', '.txt', 'README', 'CHANGELOG', 'CONTRIBUTING']:
            for doc_file in project_path.rglob(f"*{ext}*"):
                if not any(ignore in str(doc_file) for ignore in ignore_patterns):
                    doc_files.append(doc_file)
        
        # Extract from documentation
        for doc_file in doc_files[:5]:  # Limit to first 5 docs
            try:
                with open(doc_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if len(content) > 100:  # Only process substantial files
                        reqs = self.extract_from_documentation(content, doc_file.name)
                        extracted_requirements["requirements_by_file"][doc_file.name] = reqs
                        requirements_parts.append(f"## Requirements from {doc_file.name}\n{reqs}")
            except Exception as e:
                continue
        
        # Scan for source code files
        code_files = []
        for ext in file_extensions:
            for code_file in project_path.rglob(f"*{ext}"):
                if not any(ignore in str(code_file) for ignore in ignore_patterns):
                    if code_file.is_file() and code_file.stat().st_size < 100000:  # Files < 100KB
                        code_files.append(code_file)
        
        # Extract from code (sample approach - analyze key files)
        key_files = sorted(code_files, key=lambda x: x.stat().st_size, reverse=True)[:10]  # Top 10 largest files
        
        for code_file in key_files:
            try:
                with open(code_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if len(content) > 200:  # Only process substantial files
                        reqs = self.extract_from_code(content, str(code_file))
                        extracted_requirements["requirements_by_file"][code_file.name] = reqs
                        requirements_parts.append(f"## Requirements from {code_file.name}\n{reqs}")
            except Exception as e:
                continue
        
        # Combine all requirements
        extracted_requirements["combined_requirements"] = "\n\n".join(requirements_parts)
        
        return extracted_requirements
    
    def extract_from_api_spec(self, api_spec_content: str, spec_type: str = "OpenAPI") -> str:
        """
        Extract requirements from API specifications (OpenAPI, Swagger, etc.)
        
        Args:
            api_spec_content: API specification content
            spec_type: Type of specification (OpenAPI, Swagger, GraphQL, etc.)
            
        Returns:
            Extracted requirements as text
        """
        prompt = f"""Analyze the following {spec_type} API specification and extract testable requirements:

API SPECIFICATION:
{api_spec_content[:5000]}  # Limit to first 5000 chars

Extract:
1. API endpoints
2. Request/response scenarios
3. Authentication requirements
4. Error handling cases
5. Validation rules

Format as clear user stories suitable for API BDD testing:
- "As a developer, I want to test [endpoint] with [scenario] so that [expected result]"
"""
        
        try:
            requirements = self.groq_client.generate_response(prompt, self.system_prompt)
            return requirements
        except Exception as e:
            return f"Error extracting requirements from API spec: {str(e)}"
    
    def save_extracted_requirements(self, requirements: str, output_file: str = None) -> str:
        """
        Save extracted requirements to a file
        
        Args:
            requirements: Extracted requirements text
            output_file: Output file path (optional)
            
        Returns:
            Path to saved file
        """
        Config.ensure_directories()
        
        if not output_file:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(Config.REQUIREMENTS_DIR, f"extracted_requirements_{timestamp}.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        return output_file








