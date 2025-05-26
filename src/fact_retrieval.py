"""
fact_retrieval.py

This module handles retrieving and processing facts from an API.
It provides functions for retrieving facts, expanding them using AI, and extracting keywords.
"""

import requests
import json
import re
import os
import logging
import random
from typing import List, Dict, Any, Union

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_fact(api_url: str, config: Dict = None) -> str:
    """
    Retrieves a random fact from a specified API.
    
    Parameters:
        api_url (str): The URL of the API to fetch facts from.
        config (Dict): Configuration dictionary that may contain API keys or AI expansion settings.
        
    Returns:
        str: A random fact as a string.
    """
    # Check if AI expansion is enabled in the config
    ai_expansion_enabled = config.get("ai_expansion_enabled", False) if config else False
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Different APIs return data in different formats, so we need to handle various cases
        try:
            data = response.json()
            
            # Try to extract the fact from the response based on common API structures
            if isinstance(data, str):
                fact = data
            elif isinstance(data, dict):
                # Look for common keys that might contain the fact
                for key in ['text', 'fact', 'content', 'value', 'message']:
                    if key in data:
                        fact = data[key]
                        break
                else:
                    # If no common key is found, just use the first value
                    fact = list(data.values())[0]
            else:
                fact = str(data)
                
        except json.JSONDecodeError:
            # If the response is not JSON, assume it's plain text
            fact = response.text
            
        # Perform AI expansion if enabled
        if ai_expansion_enabled:
            expanded_fact = expand_fact_with_ai(fact, config)
            if expanded_fact:
                fact = expanded_fact
                
        return fact
        
    except (requests.RequestException, json.JSONDecodeError) as e:
        logging.error(f"Error retrieving fact: {e}")
        
        # Fallback: return a hard-coded fact
        fallback_facts = [
            "The shortest war in history was between Britain and Zanzibar in 1896, lasting only 38 minutes.",
            "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly good to eat.",
            "The world's oldest known living tree is a Great Basin bristlecone pine named Methuselah, estimated to be over 4,800 years old.",
            "A day on Venus is longer than a year on Venus. It takes 243 Earth days for Venus to rotate once on its axis, but only 225 Earth days to orbit the Sun.",
            "The average person will spend six months of their life waiting for red lights to turn green."
        ]
        return random.choice(fallback_facts)

def expand_fact_with_ai(fact: str, config: Dict) -> str:
    """
    Expands a fact using AI to make it more engaging and informative.
    
    Parameters:
        fact (str): The original fact.
        config (Dict): Configuration containing API keys and settings.
        
    Returns:
        str: An expanded version of the fact, or the original if expansion fails.
    """
    # Try to use Hugging Face API for AI expansion
    huggingface_api_key = config.get("huggingface_api_key", "")
    if huggingface_api_key and huggingface_api_key != "YOUR_KEY":
        try:
            api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {"Authorization": f"Bearer {huggingface_api_key}"}
            
            prompt = f"""
            Expand this fact into a 3-sentence engaging narrative. Keep it concise and include one surprising detail: "{fact}"
            """
            
            payload = {
                "inputs": prompt,
                "parameters": {"max_length": 512, "temperature": 0.7}
            }
            
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                # Extract the generated text
                expanded_fact = result[0].get("generated_text", "")
                
                # Clean up the response to extract just the expanded fact
                # This pattern may need to be adjusted based on the specific model's output format
                match = re.search(r'(?:.*?)((?:.*?\.){1,3})', expanded_fact, re.DOTALL)
                if match:
                    return match.group(1).strip()
                return expanded_fact.strip()
            
        except Exception as e:
            logging.error(f"Error expanding fact with Hugging Face API: {e}")
    
    # Fallback: Try to use the Gemini API if available
    gemini_api_key = config.get("gemini_api_key", "")
    if gemini_api_key and gemini_api_key != "YOUR_KEY":
        try:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Expand this fact into a 3-sentence engaging narrative. Keep it concise and include one surprising detail: {fact}"
                    }]
                }]
            }
            
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            expanded_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            if expanded_text:
                return expanded_text.strip()
                
        except Exception as e:
            logging.error(f"Error expanding fact with Gemini API: {e}")
    
    # Second fallback: Simple rule-based expansion
    try:
        # Add some engaging prefixes and suffixes
        prefixes = [
            "Did you know? ",
            "Here's something fascinating: ",
            "Prepare to be amazed! ",
            "This is incredible: ",
            "A mind-blowing fact: "
        ]
        
        suffixes = [
            " This has fascinated scientists for years.",
            " It's one of nature's most remarkable phenomena.",
            " Most people don't realize this amazing truth.",
            " This surprising fact changes how we see the world.",
            " Researchers continue to study this phenomenon."
        ]
        
        expanded_fact = random.choice(prefixes) + fact
        
        # Only add a suffix if the fact is relatively short
        if len(expanded_fact) < 100:
            expanded_fact += random.choice(suffixes)
            
        return expanded_fact
        
    except Exception as e:
        logging.error(f"Error in rule-based fact expansion: {e}")
    
    # If all expansion methods fail, return the original fact
    return fact

def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extracts key thematic words from the text for visual matching.
    
    Parameters:
        text (str): The text to extract keywords from.
        max_keywords (int): Maximum number of keywords to extract.
        
    Returns:
        List[str]: A list of extracted keywords.
    """
    # Convert to lowercase and remove punctuation
    text = re.sub(r'[^\w\s]', '', text.lower())
    
    # Define common stopwords to filter out
    stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what', 'with', 'by', 'for', 'to', 'from', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'don', 'should', 'now'}
    
    # Split the text into words and filter out stopwords and short words
    words = [word for word in text.split() if word not in stopwords and len(word) > 2]
    
    # Count word frequencies
    word_counts = {}
    for word in words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    
    # Sort words by frequency and get the top N keywords
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, _ in sorted_words[:max_keywords]]
    
    # If we don't have enough keywords, add some default ones
    if len(keywords) < max_keywords:
        default_keywords = ['nature', 'science', 'history', 'world', 'discovery']
        keywords.extend(default_keywords[:max_keywords - len(keywords)])
    
    return keywords