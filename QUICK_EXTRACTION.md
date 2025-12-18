# Quick Guide: Extract Requirements from Any Project

## What This Does

Automatically analyzes any project and extracts requirements to create BDD feature files - **no manual requirements needed!**

## Quick Command

```powershell
python orchestrator.py --stage extract_and_generate --project-path "C:\path\to\your\project" --feature-name my_tests
```

## How It Works

1. **Scans your project** - Analyzes code, documentation, and project files
2. **Extracts requirements** - Uses AI to identify testable features
3. **Generates feature files** - Creates `.feature` files automatically

## Example Usage

### Analyze a Python Project
```powershell
python orchestrator.py --stage extract_and_generate --project-path "C:\MyProject" --feature-name python_project
```

### Analyze Specific File Types Only
```powershell
python orchestrator.py --stage extract_and_generate --project-path "C:\MyProject" --file-extensions .py .md --feature-name python_only
```

### Extract Requirements Only (Don't Generate Features Yet)
```powershell
python orchestrator.py --stage extract_requirements --project-path "C:\MyProject"
```

## Output

- **Extracted Requirements**: `requirements/extracted_requirements_*.txt`
- **Feature File**: `features/{feature_name}.feature`

## What Gets Analyzed

✅ **Code files**: `.py`, `.js`, `.ts`, `.java`, etc.  
✅ **Documentation**: `README.md`, `.txt`, etc.  
✅ **Config files**: `.yaml`, `.json`, etc.  

❌ **Automatically ignored**: `node_modules`, `.git`, `__pycache__`, etc.

## Next Steps

After extraction, you can:
1. Review the generated feature file
2. Generate step definitions: `python orchestrator.py --stage feature_to_stepdef --feature-file features/my_tests.feature`
3. Continue with full pipeline

## See Full Documentation

For detailed information, see: **PROJECT_EXTRACTION_GUIDE.md**










