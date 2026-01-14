from google import genai
import os
from doclify.config.constants import CliConfig
from doclify.utils.utils import get_prompt

def generate_doc(code_content: str, type: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set. Please set it to use Docly.")
    
    try:
        client = genai.Client(api_key=api_key)
        
        prompt_name = "code_summary" if type == "code_summary" else "final_summary"
        prompt = get_prompt(prompt_name)
        
        response = client.models.generate_content(
            model=CliConfig.MODEL_NAME,
            contents=prompt + code_content
        )
        return response.text
            
    except Exception as e:
        raise ValueError(f"Failed to generate documentation: {e}")