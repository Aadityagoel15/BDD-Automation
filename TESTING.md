# Testing Guide

## Quick System Test

Run the automated test script to verify everything is set up correctly:

```bash
python test_system.py
```

This script checks:
- ✓ All required modules can be imported
- ✓ All dependencies are installed
- ✓ Configuration is correct
- ✓ Directories are created
- ✓ Groq API key is configured
- ✓ Groq API connection works
- ✓ All agents can be initialized
- ✓ Simple end-to-end test works

## Manual Testing Steps

### 1. Test Individual Components

#### Test Configuration
```python
from config import Config
Config.ensure_directories()
print(Config.GROQ_API_KEY[:10] + "...")  # Should show first 10 chars
```

#### Test Groq API Connection
```python
from groq_client import GroqClient

client = GroqClient()
response = client.generate_response("Say hello", "You are helpful")
print(response)  # Should print a response
```

#### Test Requirements to Feature Agent
```python
from agents.requirements_to_feature_agent import RequirementsToFeatureAgent

agent = RequirementsToFeatureAgent()
requirements = "As a user, I want to login so that I can access my account"
feature = agent.convert_requirements_to_feature(requirements, "login_test")
print(feature)
```

### 2. Test Full Pipeline

#### Using Command Line
```bash
python orchestrator.py --requirements "As a user, I want to search for products" --feature-name search_test
```

#### Using Python Script
```python
from orchestrator import BDDAutomationOrchestrator

orchestrator = BDDAutomationOrchestrator()
results = orchestrator.run_full_pipeline(
    requirements="As a user, I want to add items to cart",
    feature_name="cart_test"
)
print(results)
```

### 3. Test Individual Stages

#### Stage 1: Requirements → Feature
```python
from orchestrator import BDDAutomationOrchestrator

orchestrator = BDDAutomationOrchestrator()
result = orchestrator.run_single_stage(
    "requirements_to_feature",
    requirements="As a user, I want to checkout",
    feature_name="checkout"
)
print(result["feature_file"])
```

#### Stage 2: Feature → Step Definitions
```python
result = orchestrator.run_single_stage(
    "feature_to_stepdef",
    feature_file="features/checkout.feature"
)
print(result["step_def_file"])
```

#### Stage 3: Execution
```python
result = orchestrator.run_single_stage(
    "execution",
    feature_file="features/checkout.feature"
)
print(result["success"])
```

#### Stage 4: Reporting
```python
execution_results = {...}  # From stage 3
result = orchestrator.run_single_stage(
    "reporting",
    execution_results=execution_results
)
print(result["report_path"])
```

#### Stage 5: Defects
```python
result = orchestrator.run_single_stage(
    "defects",
    execution_results=execution_results,
    test_report=report_result
)
print(result["defects_found"])
```

## Expected Outputs

### Successful Test Run Should Show:

1. **Feature Generation**:
   ```
   ✓ Feature file created: features/login.feature
   ```

2. **Step Definition Generation**:
   ```
   ✓ Step definitions created: step_definitions/login_steps.py
   ```

3. **Test Execution**:
   ```
   ✓ Tests executed successfully
   ```

4. **Report Generation**:
   ```
   ✓ Report generated: reports/test_report_20240101_120000.json
   ✓ Summary available: reports/test_report_summary_20240101_120000.txt
   ```

5. **Defect Identification**:
   ```
   ✓ Defects identified: 0
   ```

## Troubleshooting Tests

### Issue: "GROQ_API_KEY not found"
**Solution**: 
- Create `.env` file in project root
- Add: `GROQ_API_KEY=your_actual_key_here`
- Get key from: https://console.groq.com/

### Issue: "Module not found"
**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: "behave command not found"
**Solution**:
```bash
pip install behave
```

### Issue: "Import errors"
**Solution**:
- Make sure you're running from project root directory
- Check that all files are in correct locations
- Verify Python path includes project directory

### Issue: "API connection failed"
**Solution**:
- Verify API key is correct
- Check internet connection
- Verify Groq API service is available
- Check if you've reached rate limits

## Test Files Location

After running tests, check these directories:

- `features/` - Generated feature files
- `step_definitions/` - Generated step definitions
- `reports/` - Test reports and execution results

## Continuous Testing

For ongoing testing, you can:

1. Run test script before each deployment:
   ```bash
   python test_system.py
   ```

2. Add to CI/CD pipeline (if applicable)

3. Run smoke test with minimal requirements:
   ```bash
   python orchestrator.py --requirements "Test" --feature-name smoke_test
   ```

## Performance Testing

To test performance with larger requirements:

```python
large_requirements = """
As an e-commerce user,
I want to:
- Browse products
- Search for items
- Filter results
- Add to cart
- Checkout
- Track orders
So that I can complete my shopping experience.
"""

orchestrator = BDDAutomationOrchestrator()
results = orchestrator.run_full_pipeline(large_requirements, "ecommerce_test")
```

## Validation Checklist

Before considering the system production-ready:

- [ ] All imports work
- [ ] Dependencies installed
- [ ] API key configured
- [ ] API connection successful
- [ ] All agents initialize
- [ ] Feature generation works
- [ ] Step definition generation works
- [ ] Test execution works
- [ ] Reports are generated
- [ ] Defects are identified
- [ ] Full pipeline completes end-to-end










