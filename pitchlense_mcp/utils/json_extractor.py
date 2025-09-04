"""
JSON extraction utilities for PitchLense MCP Package.

Provides functions to extract and parse JSON content from LLM responses.
"""

import re
import json
from typing import Dict, Any, Optional


def extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON content from LLM response using various methods.
    
    This function tries multiple extraction methods in order of preference:
    1. Extract content between <JSON> and </JSON> tags
    2. Extract content between ```json and ``` code blocks
    3. Extract content between ``` and ``` code blocks
    4. Try to parse the entire response as JSON
    
    Args:
        response_text: Raw response text from LLM
        
    Returns:
        Parsed JSON dictionary if successful, None if extraction fails
    """
    if not response_text or not isinstance(response_text, str):
        return None
    
    # Clean up the response text
    response_text = response_text.strip()
    
    # Method 1: Extract from <JSON> tags
    json_content = _extract_from_json_tags(response_text)
    if json_content:
        parsed = _parse_json(json_content)
        if parsed:
            return parsed
    
    # Method 2: Extract from ```json code blocks
    json_content = _extract_from_json_code_blocks(response_text)
    if json_content:
        parsed = _parse_json(json_content)
        if parsed:
            return parsed
    
    # Method 3: Extract from ``` code blocks
    json_content = _extract_from_code_blocks(response_text)
    if json_content:
        parsed = _parse_json(json_content)
        if parsed:
            return parsed
    
    # Method 4: Try to parse the entire response as JSON
    parsed = _parse_json(response_text)
    if parsed:
        return parsed
    
    return None


def _extract_from_json_tags(text: str) -> Optional[str]:
    """Extract JSON content between <JSON> and </JSON> tags."""
    pattern = r'<JSON>\s*(.*?)\s*</JSON>'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


def _extract_from_json_code_blocks(text: str) -> Optional[str]:
    """Extract JSON content from ```json code blocks."""
    pattern = r'```json\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


def _extract_from_code_blocks(text: str) -> Optional[str]:
    """Extract JSON content from ``` code blocks."""
    pattern = r'```\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(1).strip()
        # Check if it looks like JSON (starts with { or [)
        if content.startswith(('{', '[')):
            return content
    return None


def _parse_json(json_string: str) -> Optional[Dict[str, Any]]:
    """
    Parse JSON string with error handling.
    
    Args:
        json_string: JSON string to parse
        
    Returns:
        Parsed JSON dictionary if successful, None if parsing fails
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def extract_json_with_fallback(response_text: str, fallback_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract JSON from response with fallback data.
    
    Args:
        response_text: Raw response text from LLM
        fallback_data: Fallback data to return if extraction fails
        
    Returns:
        Extracted JSON or fallback data
    """
    extracted = extract_json_from_response(response_text)
    return extracted if extracted is not None else fallback_data
