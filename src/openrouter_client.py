"""
OpenRouter API Client for AI-powered task extraction
"""

import requests
import json
import re
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class OpenRouterResponse:
    """Response from OpenRouter API"""
    content: str
    model: str
    usage: Dict
    success: bool
    error: Optional[str] = None


class OpenRouterClient:
    """Client for interacting with OpenRouter API"""
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/rahulbedjavalge/todo-test-tracker",
            "X-Title": "Universal Project Todo Tracker"
        }
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models from OpenRouter"""
        try:
            response = requests.get(f"{self.base_url}/models", headers=self.headers)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            raise Exception(f"Failed to get models: {str(e)}")
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: str = "moonshotai/kimi-dev-72b:free",
                       max_tokens: int = 8000,
                       temperature: float = 0.7) -> OpenRouterResponse:
        """
        Send chat completion request to OpenRouter
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use for completion
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            OpenRouterResponse object
        """
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                return OpenRouterResponse(
                    content="",
                    model=model,
                    usage={},
                    success=False,
                    error=data['error'].get('message', 'Unknown error')
                )
            
            choice = data['choices'][0]
            content = choice['message']['content']
            usage = data.get('usage', {})
            
            return OpenRouterResponse(
                content=content,
                model=model,
                usage=usage,
                success=True
            )
            
        except requests.exceptions.RequestException as e:
            return OpenRouterResponse(
                content="",
                model=model,
                usage={},
                success=False,
                error=f"Request failed: {str(e)}"
            )
        except json.JSONDecodeError as e:
            return OpenRouterResponse(
                content="",
                model=model,
                usage={},
                success=False,
                error=f"Invalid JSON response: {str(e)}"
            )
        except Exception as e:
            return OpenRouterResponse(
                content="",
                model=model,
                usage={},
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    def extract_structured_data(self, 
                               prompt: str, 
                               model: str = "deepseek/deepseek-r1-distill-llama-70b",
                               response_format: str = "json") -> Dict:
        """
        Extract structured data using AI
        
        Args:
            prompt: The prompt to send to the AI
            model: Model to use
            response_format: Expected response format
            
        Returns:
            Parsed structured data
        """
        
        messages = [
            {
                "role": "system", 
                "content": f"You are an expert project manager and software architect. "
                          f"Respond only with valid {response_format.upper()}. "
                          f"Do not include any explanations or markdown formatting."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self.chat_completion(messages, model=model, temperature=0.3)
        
        if not response.success:
            raise Exception(f"AI request failed: {response.error}")
        
        try:
            # Try to parse as JSON
            if response_format.lower() == "json":
                # Clean the response - remove any markdown formatting and thinking tags
                content = response.content.strip()
                
                # Remove thinking tags and content between them
                content = re.sub(r'◁think▷.*?(?=\{|$)', '', content, flags=re.DOTALL)
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
                
                # Remove markdown code blocks
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                # Try to extract JSON from mixed content
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                
                return json.loads(content)
            else:
                return {"content": response.content}
                
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}\nResponse: {response.content[:500]}")
    
    def validate_model(self, model: str) -> bool:
        """Check if a model is available"""
        try:
            models = self.get_available_models()
            available_models = [m['id'] for m in models]
            return model in available_models
        except:
            # If we can't check, assume it's valid
            return True
