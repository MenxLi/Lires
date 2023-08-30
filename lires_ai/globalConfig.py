"""
Usage: 
import globalConfig as config
...
"""
import openai
from typing import Optional, Literal

openai_api_base: str = openai.api_base
fastchat_api_base: str = "http://localhost:8000/v1"

local_llm_name: Optional[str] = "Open-Orca/LlongOrca-7B-16k"
local_llm_load_bit: Literal[16, 8, 4] = 8