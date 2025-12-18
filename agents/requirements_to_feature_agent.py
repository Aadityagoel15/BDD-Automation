"""
Agent 1: Requirements to .feature file Agent
Converts requirements/user stories into Gherkin .feature files
"""
import os
from groq_client import GroqClient
from config import Config

class RequirementsToFeatureAgent:
    """Agent that converts requirements into Gherkin feature files"""
    
    def __init__(self):
        self.groq_client = GroqClient()
        self.system_prompt = """You are an expert BDD (Behavior-Driven Development) specialist. 
Your task is to convert requirements or user stories into well-structured Gherkin .feature files.

Guidelines:
1. Use proper Gherkin syntax (Feature, Scenario, Given, When, Then, And, But)
2. Write clear, readable scenarios that describe behavior
3. Include Background steps if common to multiple scenarios
4. Use Examples tables for scenario outlines when appropriate
5. Keep scenarios focused and atomic
6. Use domain language that non-technical stakeholders can understand
7. Include feature description
8. Tag scenarios appropriately (@smoke, @regression, etc.)
"""
    
    def convert_requirements_to_feature(self, requirements: str, feature_name: str = None) -> str:
        """
        Convert requirements text into a Gherkin feature file
        
        Args:
            requirements: Requirements or user story text
            feature_name: Optional name for the feature file
            
        Returns:
            Generated feature file content in Gherkin format
        """
        prompt = f"""Convert the following requirements into a Gherkin .feature file:

REQUIREMENTS:
{requirements}

Generate a complete .feature file with:
- Feature description
- Multiple scenarios covering the requirements
- Proper Gherkin syntax
- Clear, testable steps

Return ONLY the feature file content, no explanations."""
        
        feature_content = self.groq_client.generate_response(prompt, self.system_prompt)
        
        # Clean up the response to ensure it's valid Gherkin
        feature_content = self._clean_feature_content(feature_content)
        
        return feature_content
    
    def save_feature_file(self, feature_content: str, feature_name: str) -> str:
        """
        Save feature content to a .feature file
        
        Args:
            feature_content: Generated feature file content
            feature_name: Name for the feature file (without extension)
            
        Returns:
            Path to the saved feature file
        """
        Config.ensure_directories()
        
        if not feature_name:
            feature_name = "generated_feature"
        
        feature_file = os.path.join(Config.FEATURES_DIR, f"{feature_name}.feature")
        
        with open(feature_file, 'w', encoding='utf-8') as f:
            f.write(feature_content)
        
        return feature_file
    
    def _clean_feature_content(self, content: str) -> str:
        """Clean and validate feature content"""
        # Remove markdown code blocks if present
        if "```gherkin" in content:
            content = content.split("```gherkin")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Ensure it starts with Feature:
        if not content.strip().startswith("Feature:"):
            if "Feature:" in content:
                content = content[content.find("Feature:"):]
            else:
                content = "Feature: Generated Feature\n\n" + content
        
        return content




