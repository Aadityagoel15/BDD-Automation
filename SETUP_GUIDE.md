# 🚀 Quick Setup Guide for BDD Automation Framework

This guide will help you set up the BDD Automation Framework for testing **any website or API** in your company.

---

## ⏱️ Quick Start (5 minutes)

### Step 1: Clone or Copy the Project
```bash
# If using git:
git clone <repository-url>
cd "BDD Automation"

# Or simply copy the project folder to your workspace
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
1. Copy the environment template:
   ```bash
   # Windows
   copy env_template.txt .env
   
   # Linux/Mac
   cp env_template.txt .env
   ```

2. Edit `.env` file and add your Groq API key:
   ```env
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```
   Get your API key from: https://console.groq.com/

3. (Optional) Set your application URL:
   ```env
   BASE_URL=https://your-application-url.com
   ```

### Step 4: Verify Setup
```bash
python test_system.py
```

You should see: `[PASS] ALL TESTS PASSED - System is ready to use!`

### Step 5: Run Your First Test
```bash
python orchestrator.py --requirements "Navigate to https://your-app.com and click the Login button" --feature-name my_first_test
```

---

## 📋 Detailed Configuration

### Configuration Methods (Priority Order)

The framework uses the following priority for configuration:

1. **Command-line arguments** (highest priority)
2. **Requirements file** (URLs and data in requirements)
3. **`.env` file** (environment variables)
4. **`bdd.config.yaml`** (project-level defaults for web/api)
5. **Auto-detection** (fallback)

### Option 1: Configure via `.env` File (Recommended)

Create/edit `.env` in the project root:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional - Your application URL
BASE_URL=https://your-application-url.com

# Optional - Change AI model (default: llama-3.1-8b-instant)
GROQ_MODEL=llama-3.1-8b-instant
```

### Option 2: Configure via `bdd.config.yaml`

Edit `bdd.config.yaml` in the project root:

```yaml
project:
  type: web          # api | web
  base_url: https://your-application-url.com
```

### Option 3: Specify in Requirements File

When writing requirements, include the URL:

```
Navigate to the URL https://your-application-url.com/
Login with username "your_username" and password "your_password"
...
```

---

## 🎯 Testing Different Types of Applications

### Web Applications

**Setup:**
```env
BASE_URL=https://your-web-app.com
```

**Requirements Example:**
```
Navigate to the URL https://your-web-app.com/
Click on the "Products" menu
Search for "laptop"
Add "MacBook Pro" to cart
Verify cart contains 1 item
```

**Run:**
```bash
python orchestrator.py --requirements requirements/web_example.txt --feature-name web_test
```

### API Testing

**Setup:**
```env
BASE_URL=https://api.your-company.com
```

**Requirements Example:**
```
Test POST /api/users endpoint
Request body: {"name": "John Doe", "email": "john@example.com"}
Verify response status is 201
Verify response contains "user_id"
```

**Run:**
```bash
python orchestrator.py --requirements requirements/api_example.txt --feature-name api_test
```

### API Projects - Configuration

Set project type in `bdd.config.yaml`:
```yaml
project:
  type: api
  base_url: https://api.your-company.com
```

Or in requirements file, the framework will auto-detect API requirements.

---

## 📝 Writing Requirements

### Format

Requirements can be written in plain English. The framework understands:

- **Navigation**: "Navigate to the URL ..."
- **Actions**: "Click on ...", "Enter ...", "Select ..."
- **Verifications**: "Verify that ...", "Check if ...", "Should see ..."
- **Login**: "Login with username ... and password ..."

### Examples

**Simple Web Flow:**
```
Navigate to https://example.com
Click the "Sign Up" button
Enter "test@example.com" into the "email" field
Enter "password123" into the "password" field
Click the "Submit" button
Verify that the success message "Account created!" is displayed
```

**E-commerce Checkout:**
```
Navigate to https://shop.example.com
Add to cart "Wireless Mouse"
Navigate to Cart Page
Click on Checkout button
Enter first name "John", last name "Doe", and postal code "12345"
Click Continue button
Click Finish Button
Verify order confirmation text "Thank you for your order!"
```

**API Testing:**
```
Test GET /api/products endpoint
Verify response status is 200
Verify response contains array of products
Verify each product has "id", "name", and "price" fields
```

---

## 🏗️ Project Structure

```
BDD-Automation/
├── agents/                    # AI agent modules (no changes needed)
├── features/                  # Generated .feature files
│   └── steps/                 # Generated step definitions
├── reports/                   # Test reports and execution logs
├── requirements/              # Your requirements files
│   └── your_requirements.txt  # Create your own
├── config.py                  # Framework configuration
├── orchestrator.py            # Main entry point
├── test_system.py             # System verification
├── .env                       # Your configuration (create this)
├── bdd.config.yaml            # Project defaults (optional)
└── requirements.txt           # Python dependencies
```

---

## 🔧 Troubleshooting

### "GROQ_API_KEY not found"
- Create `.env` file from `env_template.txt`
- Add your Groq API key: `GROQ_API_KEY=your_key_here`

### "BASE_URL is required"
- Set `BASE_URL` in `.env`, OR
- Set `base_url` in `bdd.config.yaml`
- (Web only) Ensure the target app is reachable at that URL

### Tests fail to execute
- Verify your application is running and accessible
- Check that `BASE_URL` is correct
- Ensure Playwright is installed: `pip install playwright && playwright install`

### Import errors
- Run: `pip install -r requirements.txt`
- Ensure you're in the project root directory

### "AmbiguousStep" error
- Old step definition files may conflict
- Delete old `*_steps.py` files in `features/steps/`
- Re-run the orchestrator

---

## 💡 Best Practices

1. **Use Requirements Files**: Save your requirements in `requirements/` folder
   ```bash
   python orchestrator.py --requirements requirements/my_test.txt --feature-name my_test
   ```

2. **Organize by Feature**: Create separate requirements files for different features
   - `requirements/login_tests.txt`
   - `requirements/checkout_tests.txt`
   - `requirements/api_user_tests.txt`

3. **Version Control**: Commit `.env` to `.gitignore` (contains secrets)
   - Commit `env_template.txt` and `bdd.config.yaml`
   - Each team member creates their own `.env`

4. **Base URL Configuration**: 
   - Use `.env` for personal/local development
   - Use `bdd.config.yaml` for team/project defaults
   - Specify in requirements for one-off tests

---

## 📚 Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [HOW_TO_RUN.md](HOW_TO_RUN.md) for advanced usage
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for pipeline details
- Check [FILE_STRUCTURE.md](FILE_STRUCTURE.md) to see what files are required/generated
- Use [TESTING.md](TESTING.md) to verify the system end-to-end
- Review example requirements in [HOW_TO_RUN.md](HOW_TO_RUN.md#-run-with-your-own-requirements) for generic examples covering different scenarios

---

## ❓ Need Help?

1. Run `python test_system.py` to verify setup
2. Check configuration in `.env` and `bdd.config.yaml`
3. Review example requirements in [HOW_TO_RUN.md](HOW_TO_RUN.md#-run-with-your-own-requirements)
4. Contact your development team for support

---

**You're all set!** Start testing your applications with the BDD Automation Framework. 🎉

