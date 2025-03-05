"""
This module is deprecated. Please use llm.llm_utils instead.
Kept for backward compatibility.
"""

from util.llm import call_llm, create_default_response, extract_json_from_deepseek_response

__all__ = [
    'call_llm',
    'create_default_response',
    'extract_json_from_deepseek_response'
]
