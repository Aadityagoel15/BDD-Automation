# System Architecture

## Overview

The BDD Automation AI Agents system uses a pipeline architecture where each agent handles a specific stage of the BDD workflow. All agents communicate with Groq API for AI-powered processing.

## Pipeline Flow

```
Requirements
    ↓
[Agent 1: Requirements → Feature]
    ↓
.feature file (Gherkin)
    ↓
[Agent 2: Feature → Step Definitions]
    ↓
step_definitions.py
    ↓
[Agent 3: Execution]
    ↓
Test Results (JSON)
    ↓
[Agent 4: Reporting] ───┐
    ↓                    │
Report                   │
    ↓                    │
[Agent 5: Defects] ←─────┘
    ↓
Defect Reports
```

## Agent Details

### 1. Requirements to Feature Agent
- **Input**: Natural language requirements/user stories
- **Output**: Gherkin `.feature` file
- **AI Task**: Convert requirements into structured BDD scenarios
- **Key Files**: `agents/requirements_to_feature_agent.py`

### 2. Feature to Step Definition Agent
- **Input**: `.feature` file (Gherkin)
- **Output**: Python step definitions file
- **AI Task**: Generate Python code implementing Gherkin steps
- **Key Files**: `agents/feature_to_stepdef_agent.py`

### 3. Execution Agent
- **Input**: Feature files and step definitions
- **Output**: Test execution results (JSON, console output)
- **AI Task**: None (executes behave framework)
- **Key Files**: `agents/execution_agent.py`
- **Dependencies**: behave framework

### 4. Reporting Agent
- **Input**: Test execution results
- **Output**: Comprehensive test reports with AI insights
- **AI Task**: Analyze results and generate insights
- **Key Files**: `agents/reporting_agent.py`

### 5. Defect Agent
- **Input**: Test execution results, test reports
- **Output**: Defect reports with root cause analysis
- **AI Task**: Identify defects, analyze failures, suggest fixes
- **Key Files**: `agents/defect_agent.py`

## Core Components

### GroqClient (`groq_client.py`)
- Centralized Groq API communication
- Handles API calls, error handling, JSON parsing
- Used by all AI-powered agents

### Config (`config.py`)
- Centralized configuration management
- Environment variables handling
- Directory structure management

### Orchestrator (`orchestrator.py`)
- Coordinates all agents
- Manages pipeline execution
- Provides CLI interface

## Data Flow

1. **Requirements** → Stored in `requirements/` or passed directly
2. **Feature Files** → Generated in `features/` directory
3. **Step Definitions** → Generated in `step_definitions/` directory
4. **Execution Results** → Stored in `reports/` as JSON
5. **Test Reports** → Stored in `reports/` as JSON and TXT
6. **Defect Reports** → Stored in `reports/` as JSON and TXT

## Technology Stack

- **Language**: Python 3.8+
- **AI API**: Groq (Llama models)
- **BDD Framework**: behave
- **Configuration**: python-dotenv
- **Reporting**: JSON, TXT, HTML (via behave)

## Extensibility

### Adding New Agents
1. Create new agent class in `agents/` directory
2. Inherit from base patterns (use GroqClient)
3. Add to orchestrator pipeline
4. Update documentation

### Customizing AI Behavior
- Modify `system_prompt` in each agent
- Adjust `temperature` and `max_tokens` in Config
- Change Groq model in Config (e.g., `mixtral-8x7b-32768`)

## Error Handling

- Each agent includes try-catch blocks
- Groq API errors are caught and reported
- File operations include error handling
- Execution agent handles subprocess errors
- Results include status indicators

## Performance Considerations

- AI API calls are async-capable (can be parallelized)
- File I/O is sequential
- Test execution depends on behave performance
- Reports are generated after execution completes






