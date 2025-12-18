# Project Requirements Extraction Guide

This guide explains how to automatically extract requirements from any project and generate BDD feature files.

## Overview

The system can analyze a project and automatically:
1. **Extract requirements** from code, documentation, and project files
2. **Generate feature files** from the extracted requirements
3. **Create step definitions** (optional continuation of pipeline)

## Quick Start

### Extract Requirements and Generate Features from Project

```powershell
python orchestrator.py --stage extract_and_generate --project-path "C:\path\to\your\project" --feature-name my_project
```

This will:
1. Analyze project files (code, docs, etc.)
2. Extract testable requirements
3. Generate `.feature` files automatically

## Usage Examples

### Example 1: Analyze Python Project

```powershell
python orchestrator.py --stage extract_and_generate --project-path "C:\MyProject" --feature-name myproject_tests
```

### Example 2: Analyze Specific File Types Only

```powershell
python orchestrator.py --stage extract_and_generate --project-path "C:\MyProject" --file-extensions .py .md .txt --feature-name python_project
```

### Example 3: Extract Requirements Only (Don't Generate Features)

```powershell
python orchestrator.py --stage extract_requirements --project-path "C:\MyProject"
```

## What Gets Analyzed

### Automatically Analyzed Files:

1. **Documentation Files**:
   - README.md, README.txt
   - CHANGELOG, CONTRIBUTING
   - Any .md or .txt files

2. **Source Code Files**:
   - .py (Python)
   - .js, .ts (JavaScript/TypeScript)
   - .java (Java)
   - .yaml, .yml, .json (Configuration)

3. **API Specifications**:
   - OpenAPI/Swagger files
   - API documentation

### Automatically Ignored:

- `__pycache__`, `.git`, `node_modules`
- `venv`, `env`, `.pytest_cache`
- `coverage`, `dist`, `build`
- `.idea`, `.vscode`

## Using in Python Code

### Extract and Generate Features

```python
from orchestrator import BDDAutomationOrchestrator

orchestrator = BDDAutomationOrchestrator()

# Extract requirements from project and generate features
results = orchestrator.run_extract_and_generate_pipeline(
    project_path="C:/MyProject",
    feature_name="project_features",
    file_extensions=['.py', '.md', '.js']  # Optional
)

print(f"Feature file: {results['stages']['requirements_to_feature']['feature_file']}")
```

### Extract Requirements Only

```python
from agents.requirements_extraction_agent import RequirementsExtractionAgent

agent = RequirementsExtractionAgent()

# Extract from project directory
result = agent.extract_from_project_directory(
    project_path="C:/MyProject",
    file_extensions=['.py', '.md']
)

print("Extracted requirements:")
print(result['combined_requirements'])

# Save to file
req_file = agent.save_extracted_requirements(result['combined_requirements'])
print(f"Saved to: {req_file}")
```

### Extract from Specific Files

```python
from agents.requirements_extraction_agent import RequirementsExtractionAgent

agent = RequirementsExtractionAgent()

# Extract from documentation
with open("README.md", 'r') as f:
    doc_content = f.read()
requirements = agent.extract_from_documentation(doc_content, "README")
print(requirements)

# Extract from code
with open("app.py", 'r') as f:
    code_content = f.read()
requirements = agent.extract_from_code(code_content, "app.py")
print(requirements)

# Extract from user stories
user_stories = """
As a user, I want to login
As a user, I want to search for products
"""
requirements = agent.extract_from_user_stories(user_stories)
print(requirements)

# Extract from API spec
with open("api.yaml", 'r') as f:
    api_spec = f.read()
requirements = agent.extract_from_api_spec(api_spec, "OpenAPI")
print(requirements)
```

## Output Files

### Extraction Results:

- **Requirements File**: `requirements/extracted_requirements_YYYYMMDD_HHMMSS.txt`
  - Contains all extracted requirements organized by source file

### Generated Files:

- **Feature File**: `features/{feature_name}.feature`
  - Generated Gherkin feature file ready for BDD testing

## Customization

### Specify File Extensions

Only analyze specific file types:

```powershell
python orchestrator.py --stage extract_and_generate --project-path "C:\MyProject" --file-extensions .py .java .md
```

### Continue Full Pipeline

After extraction and feature generation, you can continue with the full pipeline:

```python
# After extraction and feature generation
feature_file = results['stages']['requirements_to_feature']['feature_file']

# Generate step definitions
stepdef_result = orchestrator.run_single_stage(
    "feature_to_stepdef",
    feature_file=feature_file
)

# Execute tests
execution_result = orchestrator.run_single_stage(
    "execution",
    feature_file=feature_file
)
```

## What Requirements Are Extracted

The AI analyzes and extracts:

1. **User Stories**: 
   - "As a [user], I want [action] so that [benefit]"

2. **Functional Requirements**:
   - What the system should do
   - Business logic requirements

3. **Test Scenarios**:
   - Edge cases
   - Error handling
   - Validation rules

4. **API Requirements** (if API specs found):
   - Endpoints
   - Request/response scenarios
   - Authentication flows

## Best Practices

1. **Clean Project**: Remove build artifacts and dependencies before extraction
2. **Documentation**: Projects with good documentation yield better requirements
3. **Code Comments**: Well-commented code helps extract requirements
4. **Review Generated Features**: Always review and refine generated feature files
5. **Iterative Approach**: Extract → Review → Refine → Generate

## Limitations

1. **Large Projects**: Very large projects may take time; system analyzes top files by size
2. **Complex Logic**: Very complex business logic may need manual refinement
3. **Binary Files**: Cannot extract from binary files
4. **Context**: Some context may be lost if code is highly modularized

## Troubleshooting

### No Requirements Extracted

- Check that project path exists
- Verify files are readable (not binary)
- Try specifying file extensions explicitly

### Too Many/Few Requirements

- Adjust file_extensions parameter
- Review extraction results and refine
- Manually add requirements if needed

### Quality Issues

- The AI extracts best-effort requirements
- Always review and refine extracted requirements
- Combine with manual requirements gathering

## Example Workflow

```powershell
# Step 1: Extract requirements and generate features
python orchestrator.py --stage extract_and_generate --project-path "C:\MyWebApp" --feature-name webapp

# Step 2: Review generated feature file
# Open: features/webapp.feature

# Step 3: Generate step definitions
python orchestrator.py --stage feature_to_stepdef --feature-file features/webapp.feature

# Step 4: Execute tests
python orchestrator.py --stage execution --feature-file features/webapp.feature
```

## Advanced Usage

### Custom Extraction Strategy

```python
from agents.requirements_extraction_agent import RequirementsExtractionAgent

agent = RequirementsExtractionAgent()

# Analyze specific files only
code_requirements = []
for file_path in ["src/main.py", "src/app.py"]:
    with open(file_path, 'r') as f:
        code = f.read()
        reqs = agent.extract_from_code(code, file_path)
        code_requirements.append(reqs)

# Combine with documentation
with open("README.md", 'r') as f:
    doc = f.read()
    doc_reqs = agent.extract_from_documentation(doc, "README")

# Combine all
all_requirements = "\n\n".join(code_requirements + [doc_reqs])
```

## Conclusion

The requirements extraction feature makes it easy to:
- ✅ Quickly understand what needs testing
- ✅ Generate feature files from any project
- ✅ Start BDD testing faster
- ✅ Ensure comprehensive test coverage

Remember: Always review and refine the extracted requirements for best results!






