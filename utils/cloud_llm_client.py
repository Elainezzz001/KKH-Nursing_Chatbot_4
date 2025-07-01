import streamlit as st
import requests
import json
import os
from typing import Dict, Optional

class CloudLLMClient:
    """Alternative LLM client for cloud deployment using OpenAI API"""
    
    def __init__(self):
        # Try to get API key from Streamlit secrets or environment
        self.api_key = self._get_api_key()
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
        self.system_message = "You are a helpful nursing chatbot for KKH (KK Women's and Children's Hospital). Only answer based on the context provided. If the context doesn't contain relevant information, politely say so and suggest the user consult with medical professionals."
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from various sources"""
        # Try Streamlit secrets first (for cloud deployment)
        try:
            return st.secrets["OPENAI_API_KEY"]
        except:
            pass
        
        # Try environment variable
        return os.getenv("OPENAI_API_KEY")
    
    def generate_response(self, user_question: str, context: str) -> Dict[str, str]:
        """Generate response using OpenAI API"""
        
        if not self.api_key:
            return {
                "success": False,
                "response": "OpenAI API key not configured. Please add your API key to use the cloud version.",
                "error": "No API key"
            }
        
        try:
            # Format the user message with context
            user_message = f"Context:\n{context}\n\nQuestion: {user_question}"
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": self.system_message
                    },
                    {
                        "role": "user", 
                        "content": user_message
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 512
            }
            
            # Make the API request
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    assistant_message = result["choices"][0]["message"]["content"]
                    
                    return {
                        "success": True,
                        "response": assistant_message.strip(),
                        "context_used": context[:200] + "..." if len(context) > 200 else context,
                        "model": self.model
                    }
                else:
                    return {
                        "success": False,
                        "response": "Sorry, I received an unexpected response format from the AI model.",
                        "error": "Invalid response format"
                    }
            else:
                error_text = response.text
                if response.status_code == 401:
                    error_msg = "Invalid API key. Please check your OpenAI API key."
                elif response.status_code == 429:
                    error_msg = "API rate limit exceeded. Please try again later."
                else:
                    error_msg = f"API error: {response.status_code}"
                
                return {
                    "success": False,
                    "response": error_msg,
                    "error": error_text
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "response": "Sorry, I can't connect to the AI service. Please check your internet connection.",
                "error": "Connection error"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "response": "Sorry, the AI service is taking too long to respond. Please try again.",
                "error": "Timeout error"
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"Sorry, an unexpected error occurred: {str(e)}",
                "error": str(e)
            }
    
    def test_connection(self) -> Dict[str, any]:
        """Test if OpenAI API is accessible"""
        if not self.api_key:
            return {
                "connected": False,
                "status": "No API key configured",
                "url": self.base_url
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Simple test request
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, are you working?"
                    }
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "connected": True,
                    "status": "OpenAI API is accessible",
                    "url": self.base_url
                }
            else:
                return {
                    "connected": False,
                    "status": f"OpenAI API responded with status {response.status_code}",
                    "url": self.base_url
                }
                
        except Exception as e:
            return {
                "connected": False,
                "status": f"Error testing connection: {str(e)}",
                "url": self.base_url
            }
