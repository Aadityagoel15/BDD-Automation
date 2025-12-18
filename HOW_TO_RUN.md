# 🚀 How to Run BDD Automation AI Agents

This project provides an **AI‑driven BDD automation framework** that converts requirements into executable tests.

> ✅ **Important Design Principle**
>
> * This framework is **configuration‑driven**
> * Users should **only configure environment variables or config files**
> * **No framework code changes are required** to test against real APIs

---

## 1️⃣ Clone and enter the project

```powershell
git clone <your-github-url>.git
cd "BDD Automation"
```

---

## 2️⃣ Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 3️⃣ Configure environment (`.env`) ✅ **PRIMARY CONFIGURATION POINT**

Create a `.env` file in the project root (you can copy from `env_template.txt`):

```text
GROQ_API_KEY=your_actual_groq_api_key_here

# Required ONLY when executing against a real API
BASE_URL=http://localhost:8080
```

### 🔑 Notes

* `GROQ_API_KEY` is **mandatory**
* `BASE_URL` is **optional**

  * Required only if you want to hit a **real running API**
  * If not provided, test generation still works, but execution may fail

---

## 4️⃣ Optional: Configure via `bdd.config.yaml`

You may optionally define project‑level defaults using `bdd.config.yaml`:

```yaml
project:
  type: api        # api | web | mobile | data | backend
  base_url: http://localhost:8080
```

### 📌 Precedence Rule

1. `.env` values (highest priority)
2. `bdd.config.yaml`
3. Auto‑detection (fallback)

> ⚠️ You **do NOT need to edit this file** unless you want repository‑level defaults.

---

## 5️⃣ Verify system setup

From the project root:

```powershell
python test_system.py
```

Expected output:

```text
[PASS] ALL TESTS PASSED - System is ready to use!
```

If this fails:

* Verify Python version
* Run `pip install -r requirements.txt`
* Ensure `.env` exists and contains `GROQ_API_KEY`

---

## 6️⃣ Run the full AI pipeline (example)

This demonstrates the complete flow:
**requirements → feature → step definitions → execution → reports → defects**

```powershell
python orchestrator.py \
  --requirements "As a user, I want to authenticate using valid credentials so that I can access protected resources." \
  --feature-name login_feature
```

### What this does

* Generates a feature file → `features/login_feature.feature`
* Generates step definitions → `features/steps/login_feature_steps.py`
* Executes Behave tests against `BASE_URL` (if provided)
* Writes reports and defect summaries under `reports/`

> ⚠️ If no API is running at `BASE_URL`, Behave may report scenario errors, but **the pipeline itself will still complete successfully**.

---

## 7️⃣ Run with your own requirements

### Inline requirements

```powershell
python orchestrator.py --requirements "Your API requirements here" --feature-name my_feature
```

### Requirements from file

```powershell
python orchestrator.py --requirements requirements.txt --feature-name my_feature
```

---

## 8️⃣ Extract requirements from an existing project (optional)

```powershell
python orchestrator.py \
  --stage extract_and_generate \
  --project-path "C:\\Path\\To\\YourProject" \
  --feature-name project_tests
```

This will:

* Analyze code / documentation
* Extract testable requirements
* Generate feature files under `features/`

> ❌ This mode **does NOT execute Behave tests** automatically.

---

## 9️⃣ Output locations

| Artifact         | Location                                 |
| ---------------- | ---------------------------------------- |
| Feature files    | `features/{feature_name}.feature`        |
| Step definitions | `features/steps/{feature_name}_steps.py` |
| Execution report | `reports/execution_report_*.json`        |
| AI test report   | `reports/test_report_*.json`             |
| Summary report   | `reports/test_report_summary_*.txt`      |
| Defect report    | `reports/defects_*.json`                 |

---

## 🔟 What NOT to modify ❌ (Critical)

Do **NOT** edit:

* `agents/`
* `features/*.feature`
* `features/steps/*.py`
* `orchestrator.py`
* Base step helpers under `features/steps/base/`

✔️ **Only configure via `.env` or `bdd.config.yaml`**

---

## 🔧 Troubleshooting (Quick)

### Module not found / import error

```powershell
pip install -r requirements.txt
```

---

### Groq API errors

* Ensure `.env` exists
* Ensure `GROQ_API_KEY` is valid

---

### Behave execution errors

* Ensure `BASE_URL` points to a running API
* Or run pipeline only for generation and ignore execution failures

---

## ✅ Summary

* ✔️ Plug‑and‑play for company teams
* ✔️ Safe for real API testing
* ✔️ No framework code changes required
* ✔️ Configuration‑driven and scalable

---

For deeper details, see:

* `README.md` – high‑level overview
* `QUICKSTART.md` – short quickstart
* `PROJECT_EXTRACTION_GUIDE.md` – extracting from projects
* `REPORTS_AND_DEFECTS.md` – understanding reports and defects
