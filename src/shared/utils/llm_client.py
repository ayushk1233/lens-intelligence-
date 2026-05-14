import os
from typing import Type
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_structured_llm(schema: Type[BaseModel], model_name: str = "gpt-4o-mini"):
    """
    Returns an LLM bound to a specific Pydantic schema using OpenRouter.
    """
    
    # OpenRouter requires the 'openai/' prefix to route to OpenAI's models
    or_model_id = "openai/gpt-4o-mini"
    
    print(f"🔧 [DEBUG] Routing LLM request to OpenRouter: {or_model_id}")
    
    # Instantiate the OpenRouter client
    llm = ChatOpenAI(
        model=or_model_id,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={
            "HTTP-Referer": "https://pulse.internal", 
            "X-Title": "PULSE LENS Agent" 
        }
    )

    # Bind the Pydantic schema and return
    return llm.with_structured_output(schema)