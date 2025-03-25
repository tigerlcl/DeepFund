from util.logger import logger
from util.llm_model import get_model

def agent_call(prompt, llm_config, pydantic_model, max_retries: int = 3):
    """
    Makes an agent call with retry logic.
    
    Args:
        prompt: The prompt to send to the LLM
        llm_config: Configuration for the LLM   
        pydantic_model: The Pydantic model to use for the output
        max_retries: Maximum number of retries (default: 3)
    Returns:
        An instance of the pydantic_model with defaults if error occurs
    """
        
    # Get the model
    llm = get_model(llm_config)
    llm = llm.with_structured_output(pydantic_model)
    
    # Call the LLM with retries
    for attempt in range(max_retries):
        try:
            result = llm.invoke(prompt)
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Error in LLM call after {max_retries} attempts: {e}")
                # Use model's default values when error occurs
                return pydantic_model()