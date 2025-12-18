"""
System Test Script - Validates BDD Automation AI Agents setup
Run this script to verify everything is configured correctly
"""
import os
import sys
from pathlib import Path

# Use ASCII-friendly symbols for Windows compatibility
PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        from config import Config
        from groq_client import GroqClient
        from agents.requirements_to_feature_agent import RequirementsToFeatureAgent
        from agents.feature_to_stepdef_agent import FeatureToStepDefAgent
        from agents.execution_agent import ExecutionAgent
        from agents.reporting_agent import ReportingAgent
        from agents.defect_agent import DefectAgent
        from orchestrator import BDDAutomationOrchestrator
        print(f"{PASS} All imports successful")
        return True
    except ImportError as e:
        print(f"{FAIL} Import error: {e}")
        return False

def test_dependencies():
    """Test if all required packages are installed"""
    print("\nTesting dependencies...")
    required_packages = {
        'groq': 'groq',
        'dotenv': 'python-dotenv',
        'behave': 'behave',
    }
    
    all_ok = True
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"{PASS} {package} installed")
        except ImportError:
            print(f"{FAIL} {package} not installed. Run: pip install {package}")
            all_ok = False
    
    return all_ok

def test_configuration():
    """Test configuration and environment variables"""
    print("\nTesting configuration...")
    try:
        from config import Config
        
        # Test directory creation
        Config.ensure_directories()
        print(f"{PASS} Directories created/verified")
        
        # Check if API key is set
        if Config.GROQ_API_KEY:
            print(f"{PASS} GROQ_API_KEY is set (length: {len(Config.GROQ_API_KEY)} characters)")
        else:
            print(f"{WARN} GROQ_API_KEY not found in environment")
            print("  Please create a .env file with: GROQ_API_KEY=your_key_here")
            return False
        
        # Check directory paths
        directories = [
            Config.FEATURES_DIR,
            Config.STEP_DEFINITIONS_DIR,
            Config.REPORTS_DIR,
            Config.REQUIREMENTS_DIR
        ]
        for directory in directories:
            if os.path.exists(directory):
                print(f"{PASS} Directory exists: {os.path.basename(directory)}")
            else:
                print(f"{FAIL} Directory missing: {directory}")
                return False
        
        return True
    except Exception as e:
        print(f"{FAIL} Configuration error: {e}")
        return False

def test_groq_connection():
    """Test Groq API connection with a simple call"""
    print("\nTesting Groq API connection...")
    try:
        from groq_client import GroqClient
        
        client = GroqClient()
        # Make a simple test call
        response = client.generate_response(
            "Say 'API connection successful' in one sentence.",
            "You are a helpful assistant."
        )
        if response and len(response) > 0:
            print(f"{PASS} Groq API connection successful")
            print(f"  Response preview: {response[:100]}...")
            return True
        else:
            print(f"{FAIL} Groq API returned empty response")
            return False
    except ValueError as e:
        print(f"{FAIL} Configuration error: {e}")
        print("  Make sure GROQ_API_KEY is set in .env file")
        return False
    except Exception as e:
        print(f"{FAIL} Groq API connection failed: {e}")
        return False

def test_agents_initialization():
    """Test if all agents can be initialized"""
    print("\nTesting agent initialization...")
    try:
        from agents.requirements_to_feature_agent import RequirementsToFeatureAgent
        from agents.feature_to_stepdef_agent import FeatureToStepDefAgent
        from agents.execution_agent import ExecutionAgent
        from agents.reporting_agent import ReportingAgent
        from agents.defect_agent import DefectAgent
        
        # Test initialization (will fail if Groq client can't be created)
        try:
            req_agent = RequirementsToFeatureAgent()
            print(f"{PASS} RequirementsToFeatureAgent initialized")
        except Exception as e:
            print(f"{FAIL} RequirementsToFeatureAgent failed: {e}")
            return False
        
        try:
            stepdef_agent = FeatureToStepDefAgent()
            print(f"{PASS} FeatureToStepDefAgent initialized")
        except Exception as e:
            print(f"{FAIL} FeatureToStepDefAgent failed: {e}")
            return False
        
        exec_agent = ExecutionAgent()
        print(f"{PASS} ExecutionAgent initialized")
        
        try:
            report_agent = ReportingAgent()
            print(f"{PASS} ReportingAgent initialized")
        except Exception as e:
            print(f"{FAIL} ReportingAgent failed: {e}")
            return False
        
        try:
            defect_agent = DefectAgent()
            print(f"{PASS} DefectAgent initialized")
        except Exception as e:
            print(f"{FAIL} DefectAgent failed: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"{FAIL} Agent initialization error: {e}")
        return False

def test_end_to_end_simple():
    """Test a simple end-to-end flow (requires API key)"""
    print("\nTesting simple end-to-end flow...")
    try:
        from agents.requirements_to_feature_agent import RequirementsToFeatureAgent
        
        agent = RequirementsToFeatureAgent()
        simple_requirement = "As a user, I want to click a button so that I can submit a form."
        
        print("  Generating feature from simple requirement...")
        feature_content = agent.convert_requirements_to_feature(simple_requirement, "test_feature")
        
        if feature_content and "Feature:" in feature_content:
            print(f"{PASS} Feature generation successful")
            
            # Save and verify
            feature_file = agent.save_feature_file(feature_content, "test_feature")
            if os.path.exists(feature_file):
                print(f"{PASS} Feature file saved: {os.path.basename(feature_file)}")
                
                # Clean up test file
                try:
                    os.remove(feature_file)
                    print(f"{PASS} Test file cleaned up")
                except:
                    pass
                
                return True
            else:
                print(f"{FAIL} Feature file was not saved")
                return False
        else:
            print(f"{FAIL} Feature generation failed - invalid content")
            return False
            
    except Exception as e:
        print(f"{FAIL} End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("BDD Automation AI Agents - System Test")
    print("=" * 80)
    
    results = {
        "imports": test_imports(),
        "dependencies": test_dependencies(),
        "configuration": test_configuration(),
    }
    
    # Only test API-dependent features if basic setup is OK
    if all([results["imports"], results["dependencies"], results["configuration"]]):
        print("\n" + "=" * 80)
        print("Testing API-dependent features...")
        print("=" * 80)
        
        results["groq_connection"] = test_groq_connection()
        results["agent_init"] = test_agents_initialization()
        
        if results.get("groq_connection"):
            results["end_to_end"] = test_end_to_end_simple()
        else:
            results["end_to_end"] = False
            print(f"\n{WARN} Skipping end-to-end test (API connection failed)")
    else:
        print(f"\n{WARN} Skipping API-dependent tests (basic setup incomplete)")
        results["groq_connection"] = False
        results["agent_init"] = False
        results["end_to_end"] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = f"{PASS} PASS" if passed else f"{FAIL} FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 80)
    
    if all_passed:
        print(f"{PASS} ALL TESTS PASSED - System is ready to use!")
        print("\nNext steps:")
        print("1. Run: python orchestrator.py --requirements 'Your requirements here' --feature-name test")
        print("2. Or run: python example_usage.py")
        return 0
    else:
        print(f"{FAIL} SOME TESTS FAILED - Please fix the issues above")
        
        if not results.get("dependencies"):
            print("\nTip: Install missing dependencies with: pip install -r requirements.txt")
        
        if not results.get("configuration"):
            print("\nTip: Create a .env file with your GROQ_API_KEY")
            print("   See env_template.txt for reference")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())

