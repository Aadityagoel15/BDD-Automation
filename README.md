# BDD Automation AI Agents

An intelligent BDD (Behavior-Driven Development) automation system powered by Groq AI. This system automates the complete BDD workflow from requirements to defect identification using specialized AI agents.

## Overview

The system consists of 5 specialized AI agents that work together in a pipeline:

1. **Requirements to Feature Agent**: Converts requirements/user stories into Gherkin `.feature` files
2. **Feature to Step Definition Agent**: Generates Python step definitions from feature files
3. **Execution Agent**: Executes BDD tests using the behave framework
4. **Reporting Agent**: Generates comprehensive test execution reports with AI-powered insights
5. **Defect Agent**: Analyzes failures and creates detailed defect reports

## Features

- 🤖 AI-powered requirement analysis and feature file generation
- 📝 Automatic step definition generation
- 🚀 Automated test execution
- 📊 Comprehensive reporting with AI insights
- 🐛 Intelligent defect identification and analysis
- 🔄 Complete pipeline automation

## Prerequisites

- Python 3.8 or higher
- Groq API key ([Get one here](https://console.groq.com/))

## Installation

1. Clone or navigate to the project directory:
```bash
cd "C:\Users\AADITYA\Desktop\BDD Automation"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Project Structure

```
BDD Automation/
├── agents/                          # AI agent modules
│   ├── __init__.py
│   ├── requirements_to_feature_agent.py
│   ├── feature_to_stepdef_agent.py
│   ├── execution_agent.py
│   ├── reporting_agent.py
│   └── defect_agent.py
├── features/                        # Generated .feature files
├── step_definitions/                # Generated step definitions
├── reports/                         # Test reports and defect logs
├── requirements/                    # Input requirements files
├── config.py                        # Configuration settings
├── groq_client.py                   # Groq API client
├── orchestrator.py                  # Main orchestrator
├── behave.ini                       # Behave configuration
└── requirements.txt                 # Python dependencies
```

## Usage

### Full Pipeline (All Stages)

Run the complete pipeline from requirements to defect identification:

```bash
python orchestrator.py --requirements "As a user, I want to login so that I can access my account" --feature-name login_feature
```

Or use a requirements file:

```bash
python orchestrator.py --requirements requirements/user_story.txt --feature-name login_feature
```

### Individual Stages

#### 1. Requirements to Feature File

```python
from agents.requirements_to_feature_agent import RequirementsToFeatureAgent

agent = RequirementsToFeatureAgent()
requirements = "As a user, I want to search for products..."
feature_content = agent.convert_requirements_to_feature(requirements, "search_feature")
feature_file = agent.save_feature_file(feature_content, "search_feature")
```

#### 2. Feature File to Step Definitions

```python
from agents.feature_to_stepdef_agent import FeatureToStepDefAgent

agent = FeatureToStepDefAgent()
step_def_content = agent.generate_step_definitions("features/search_feature.feature")
step_def_file = agent.save_step_definitions(step_def_content, "search_feature")
```

#### 3. Execute Tests

```python
from agents.execution_agent import ExecutionAgent

agent = ExecutionAgent()
results = agent.execute_tests(feature_file="features/search_feature.feature")
```

#### 4. Generate Reports

```python
from agents.reporting_agent import ReportingAgent

agent = ReportingAgent()
report = agent.generate_report(execution_results)
```

#### 5. Identify Defects

```python
from agents.defect_agent import DefectAgent

agent = DefectAgent()
defects = agent.identify_defects(execution_results, test_report)
```

### Command Line Options

```bash
python orchestrator.py [OPTIONS]

Options:
  --requirements TEXT    Requirements text or path to requirements file
  --feature-name TEXT    Name for the feature file
  --stage TEXT          Pipeline stage to run (requirements_to_feature, 
                        feature_to_stepdef, execution, reporting, defects, full)
  --feature-file TEXT   Path to feature file (for stage-specific runs)
```

## Configuration

Edit `config.py` to customize:

- Groq model selection (default: `llama-3.1-70b-versatile`)
- Temperature for AI responses (default: 0.7)
- Max tokens (default: 4096)
- Directory paths

## Example Workflow

1. **Provide Requirements**:
   ```
   "As an e-commerce user, I want to add items to my shopping cart 
   so that I can purchase multiple products at once."
   ```

2. **AI Agent 1** generates:
   ```gherkin
   Feature: Shopping Cart
     As an e-commerce user
     I want to add items to my shopping cart
     So that I can purchase multiple products at once

     Scenario: Add single item to cart
       Given I am on the product page
       When I click "Add to Cart"
       Then the item should be added to my cart
   ```

3. **AI Agent 2** generates Python step definitions

4. **AI Agent 3** executes the tests

5. **AI Agent 4** generates comprehensive reports

6. **AI Agent 5** identifies and analyzes any defects

## Output Files

All outputs are saved in their respective directories:

- **Features**: `features/*.feature`
- **Step Definitions**: `step_definitions/*_steps.py`
- **Execution Reports**: `reports/execution_report_*.json` and `*.html`
- **Test Reports**: `reports/test_report_*.json` and `test_report_summary_*.txt`
- **Defect Reports**: `reports/defects_*.json` and `defect_report_*.txt`

## Testing the System

### Quick System Test

Run the automated test script to verify everything is set up correctly:

```bash
python test_system.py
```

This will check:
- ✓ All imports work
- ✓ Dependencies are installed
- ✓ Configuration is correct
- ✓ Groq API connection works
- ✓ All agents can be initialized
- ✓ Simple end-to-end test passes

### Manual Testing

Test the full pipeline with a simple requirement:

```bash
python orchestrator.py --requirements "As a user, I want to click a button so that I can submit a form" --feature-name test_feature
```

For detailed testing instructions, see [TESTING.md](TESTING.md)

## Troubleshooting

1. **Groq API Key Error**: Ensure your `.env` file contains a valid `GROQ_API_KEY`
2. **Import Errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`
3. **Behave Not Found**: Install behave: `pip install behave`
4. **Module Not Found**: Ensure you're running from the project root directory
5. **Test Script Fails**: Run `python test_system.py` to identify specific issues

## Extending the System

### Adding Custom Agents

Create a new agent in the `agents/` directory:

```python
from groq_client import GroqClient

class CustomAgent:
    def __init__(self):
        self.groq_client = GroqClient()
    
    def process(self, input_data):
        # Your agent logic here
        pass
```

### Customizing Prompts

Each agent has a `system_prompt` that guides the AI. Modify these in the agent files to customize behavior.

## License

This project is for internal company use.

## Support

For issues or questions, contact your development team.

