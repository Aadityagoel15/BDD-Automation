## How to Run BDD Automation AI Agents

### 1. Clone and enter the project

```powershell
git clone <your-github-url>.git
cd "BDD Automation"
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment (.env)

Create a `.env` file in the project root (you can copy from `env_template.txt`):

```text
GROQ_API_KEY=your_actual_groq_api_key_here
# Optional, for API projects
BASE_URL=http://localhost:8080
```

If you want to override project type or base URL via config, edit `bdd.config.yaml`:

```yaml
project:
  type: api        # api | web | mobile | data | backend
  base_url: http://localhost:8080
```

### 4. Verify everything is set up correctly

From the project root:

```powershell
python test_system.py
```

You should see all checks `[PASS]` and a final line:

```text
[PASS] ALL TESTS PASSED - System is ready to use!
```

If this fails, fix what it reports (missing deps, missing `GROQ_API_KEY`, etc.) before continuing.

### 5. Run the full AI pipeline with a simple example

This demonstrates the whole flow: requirements → feature → step definitions → execution → reports → defects.

```powershell
python orchestrator.py --requirements "As a user, I want to click a button so that I can submit a form." --feature-name sample_feature
```

What this does:

- Generates a feature file: `features/sample_feature.feature`
- Generates step definitions: `features/steps/sample_feature_steps.py`
- Executes Behave tests against your `BASE_URL`
- Writes reports and defect summaries under `reports/`

Note: If there is no real API running at `BASE_URL`, Behave will report scenario errors, but the pipeline itself should still complete successfully.

### 6. Run with your own requirements

Replace the sample requirement text with your own:

```powershell
python orchestrator.py --requirements "Your requirements or user stories here" --feature-name my_feature
```

Or point to a file containing your requirements:

```powershell
python orchestrator.py --requirements "requirements.txt" --feature-name my_feature
```

### 7. Extract requirements from an existing project (optional)

If you want to point the system at an existing codebase and generate tests:

```powershell
python orchestrator.py --stage extract_and_generate --project-path "C:\Path\To\YourProject" --feature-name project_tests
```

This will:

- Extract requirements from the target project
- Generate a feature file under `features/`
- (For this stage only, it does **not** automatically execute Behave tests)

### 8. Where to look for outputs

- **Feature files**: `features/{feature_name}.feature`
- **Step definitions**: `features/steps/{feature_name}_steps.py`
- **Execution reports**: `reports/execution_report_*.json`
- **AI test reports**: `reports/test_report_*.json` and `test_report_summary_*.txt`
- **Defect reports**: `reports/defects_*.json` and `defect_report_*.txt`

### 9. Troubleshooting (quick)

- **Module not found / import errors**

  ```powershell
  pip install -r requirements.txt
  ```

- **`GROQ_API_KEY not found` or Groq errors**

  - Ensure `.env` exists in the project root
  - Ensure it contains: `GROQ_API_KEY=your_key_here`

- **Running from the wrong directory**

  Always run commands from the project root:

  ```powershell
  cd "BDD Automation"
  python orchestrator.py --help
  ```

For deeper details, also see:

- `README.md` – high-level overview
- `QUICKSTART.md` – short quickstart
- `PROJECT_EXTRACTION_GUIDE.md` – extracting from projects
- `REPORTS_AND_DEFECTS.md` – understanding reports and defects
