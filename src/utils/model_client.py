from together import Together
from typing import List, Dict, Any
from src.utils.constants import DEFAULT_MODEL

# Initialize the Together client
client = Together()

def get_model_response(messages: List[Dict[str, str]], model_name: str = DEFAULT_MODEL) -> str:
    """
    Get a response from the language model.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model_name: Name of the model to use (defaults to the value in constants)
        
    Returns:
        The model's response text
    """
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
    )
    
    return response.choices[0].message.content

def get_completion(prompt: str, model_name: str = DEFAULT_MODEL) -> str:
    """
    Get a completion from the language model using a simple prompt.
    
    Args:
        prompt: The prompt text
        model_name: Name of the model to use
        
    Returns:
        The model's response text
    """
    messages = [
        {"role": "user", "content": prompt}
    ]
    return get_model_response(messages, model_name) 