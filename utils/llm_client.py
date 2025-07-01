import requests
import json
from typing import Dict, Optional

class LLMClient:
    """Client for interacting with LM Studio OpenHermes model"""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1/chat/completions"):
        self.base_url = base_url
        self.system_message = "You are a helpful nursing chatbot for KKH (KK Women's and Children's Hospital). Only answer based on the context provided. If the context doesn't contain relevant information, politely say so and suggest the user consult with medical professionals."
    
    def generate_response(self, user_question: str, context: str) -> Dict[str, str]:
        """
        Generate response using OpenHermes model
        
        Args:
            user_question: The user's question
            context: Relevant context from the knowledge base
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Format the user message with context
            user_message = f"Context:\n{context}\n\nQuestion: {user_question}"
            
            # Prepare the API request
            payload = {
                "model": "openhermes",  # Default model name in LM Studio
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
                "max_tokens": 512,
                "stream": False
            }
            
            # Make the API request
            response = requests.post(
                self.base_url,
                headers={"Content-Type": "application/json"},
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
                        "model": result.get("model", "openhermes")
                    }
                else:
                    return {
                        "success": False,
                        "response": "Sorry, I received an unexpected response format from the AI model.",
                        "error": "Invalid response format"
                    }
            else:
                return {
                    "success": False,
                    "response": f"Sorry, I'm having trouble connecting to the AI model. Please make sure LM Studio is running and accessible at {self.base_url}",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "response": "Sorry, I can't connect to the AI model. Please make sure LM Studio is running on localhost:1234 with the OpenHermes model loaded.",
                "error": "Connection error"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "response": "Sorry, the AI model is taking too long to respond. Please try again.",
                "error": "Timeout error"
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"Sorry, an unexpected error occurred: {str(e)}",
                "error": str(e)
            }
    
    def test_connection(self) -> Dict[str, any]:
        """Test if LM Studio is accessible"""
        try:
            # Simple test request
            payload = {
                "model": "openhermes",
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
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "connected": True,
                    "status": "LM Studio is running and accessible",
                    "url": self.base_url
                }
            else:
                return {
                    "connected": False,
                    "status": f"LM Studio responded with status {response.status_code}",
                    "url": self.base_url
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "connected": False,
                "status": "Cannot connect to LM Studio. Make sure it's running on localhost:1234",
                "url": self.base_url
            }
        except Exception as e:
            return {
                "connected": False,
                "status": f"Error testing connection: {str(e)}",
                "url": self.base_url
            }
