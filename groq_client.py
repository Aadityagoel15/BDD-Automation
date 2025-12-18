"""
Groq API Client for AI Agent Communication
"""
import json
from groq import Groq
from config import Config

class GroqClient:
    """Client for interacting with Groq API"""
    
    def __init__(self):
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.temperature = Config.TEMPERATURE
        self.max_tokens = Config.MAX_TOKENS
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate response from Groq API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            
        Returns:
            Generated response text
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling Groq API: {str(e)}")
    
    def generate_structured_response(self, prompt: str, system_prompt: str = None) -> dict:
        """
        Generate structured JSON response
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            
        Returns:
            Parsed JSON response
        """
        response_text = self.generate_response(prompt, system_prompt)
        try:
            # Try to extract JSON from response if wrapped in markdown
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            return {"response": response_text}










