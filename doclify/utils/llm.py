import re
import json
import os
import litellm
from doclify.config.constants import LiteLLMConfig
from doclify.utils.utils import get_prompt
from pydantic import BaseModel
from typing import Optional, Type, Any, Union, Dict
from doclify.utils.logger import get_logger
from doclify.schema.schema import LLMConfig

logger = get_logger(__name__)

# Configure litellm to be quiet unless there's an error
litellm.success_callback = []
litellm.failure_callback = []

def parse_json_response(text: str) -> str:
    """
    Extracts JSON from a string that might contain markdown code blocks.
    """
    # Try to find content within ```json ... ``` blocks
    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()
    
    # Fallback: remove simple ``` markers if present at start/end
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```[a-z]*\n?', '', cleaned)
    if cleaned.endswith("```"):
        cleaned = re.sub(r'\n?```$', '', cleaned)
    
    return cleaned.strip()

def generate_doc(
    code_content: str, 
    type: str, 
    json_format: Optional[Type[Any]] = None,
    llm_config: Optional[LLMConfig] = None
) -> Union[str, Any]:    
    try:
        # Determine model to use
        raw_model = llm_config.model if llm_config else LiteLLMConfig.DEFAULT_MODEL
        provider_override = llm_config.provider if llm_config else None
        
        # Resolve full model name for LiteLLM
        if "/" in raw_model:
            model = raw_model
        else:
            # Check the map (Iterate through the new provider -> [models] structure)
            provider = provider_override
            if not provider:
                for p, models in LiteLLMConfig.MODEL_MAP.items():
                    if raw_model in models:
                        provider = p
                        break
            
            if provider:
                model = f"{provider}/{raw_model}"
            else:
                # Default fallback or assume gemini
                model = f"gemini/{raw_model}"
        
        logger.info(f"Resolved model: {model} (from raw: {raw_model})")
        
        prompt_name = type
        prompt = get_prompt(prompt_name)
        
        messages = [
            {"role": "user", "content": prompt + code_content}
        ]

        if json_format:
            # LiteLLM supports response_format for structured output
            response = litellm.completion(
                model=model,
                messages=messages,
                response_format=json_format # or json_format.model_json_schema() depending on version
            )
            raw_text = response.choices[0].message.content
            logger.info(f"LLM call successful (Structured Output). Model: {model}")
            
            try:
                # Use pydantic validation if it's a model
                if hasattr(json_format, "model_validate_json"):
                    return json_format.model_validate_json(raw_text)
                return json.loads(raw_text)
            except Exception as parse_err:
                logger.warning(f"Direct JSON parse failed, attempting loose extraction: {parse_err}")
                extracted = parse_json_response(raw_text)
                if hasattr(json_format, "model_validate_json"):
                    return json_format.model_validate_json(extracted)
                return json.loads(extracted)
            
        else:
            response = litellm.completion(
                model=model,
                messages=messages
            )
            raw_text = response.choices[0].message.content
            logger.info(f"LLM call successful (Standard Output). Model: {model}")
            
            # For non-json responses, we still might want to strip markdown blocks if they enclose the whole response
            return parse_json_response(raw_text)
            
    except Exception as e:
        logger.error(f"Failed to generate documentation: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to generate documentation: {e}")
