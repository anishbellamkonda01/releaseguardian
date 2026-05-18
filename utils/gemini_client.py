"""
Gemini Client Setup
This file creates the connection to Google's Gemini AI.
Every agent imports from here.
"""
import os
import json
import pathlib
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load the API key from .env file (for local development)
load_dotenv(pathlib.Path(__file__).resolve().parent.parent / ".env")

# Try Streamlit secrets first (for cloud), then .env (for local)
try:
    import streamlit as st
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
except Exception:
    api_key = None

# Fall back to .env / environment variable
if not api_key:
    api_key = os.getenv("GOOGLE_API_KEY")

# Check if the key exists
if not api_key or api_key == "paste-your-api-key-here":
    raise ValueError(
        "GOOGLE_API_KEY not found! "
        "Add it to Streamlit secrets or your .env file."
    )

# Create the Gemini client
client = genai.Client(api_key=api_key)

# Model names
FLASH_MODEL = "gemini-2.5-flash-lite"    # Fast, good for extraction and generation
PRO_MODEL = "gemini-2.5-flash-lite"      # Using Flash for both to stay on free tier
# If you have paid access, change PRO_MODEL to "gemini-2.5-pro"


def call_gemini(prompt, model=FLASH_MODEL, temperature=0.3, system_instruction=None):
    """
    Send a prompt to Gemini and get a response.

    Parameters:
    - prompt: The text you want to send to Gemini
    - model: Which model to use
    - temperature: 0 = focused/deterministic, 1 = creative/random
    - system_instruction: Optional instructions that set the AI's behavior

    Returns:
    - The text response from Gemini
    """
    try:
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=8192,
        )

        # Add system instruction if provided
        if system_instruction:
            config.system_instruction = system_instruction

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        return response.text

    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return None


def call_gemini_json(prompt, model=FLASH_MODEL, temperature=0.2, system_instruction=None):
    """
    Send a prompt to Gemini and get a JSON response back.
    This is specifically for agents that need structured output.

    Returns:
    - A Python dictionary (parsed JSON), or None if it fails
    """
    result = call_gemini(prompt, model, temperature, system_instruction)

    if result is None:
        return None

    try:
        # Clean up common issues with Gemini's JSON output
        cleaned = result.strip()

        # Remove markdown code blocks if Gemini wraps the JSON in them
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # If it still doesn't start with { or [, try to find JSON in the text
        if not cleaned.startswith("{") and not cleaned.startswith("["):
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                cleaned = cleaned[start:end + 1]
            else:
                print(f"Could not find JSON in response: {cleaned[:200]}")
                return None

        # Parse and return
        return json.loads(cleaned)

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from Gemini: {e}")
        print(f"Raw response was: {result[:500]}")
        return None
