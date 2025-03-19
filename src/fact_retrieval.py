import requests
import string

def get_fact(api_url: str) -> str:
    """
    Retrieves a fact from the provided API URL.

    Parameters:
        api_url (str): The endpoint URL for fetching a fact.

    Returns:
        str: The retrieved fact text.

    Raises:
        Exception: If the API request fails.
    """
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

def extract_keywords(fact_text: str) -> list:
    """
    Extracts key thematic words from the fact text.

    The algorithm converts the text to lowercase, removes punctuation,
    splits it into words, and then filters out common stopwords and short words.
    It returns up to three unique keywords that can be used for thematic matching.

    Parameters:
        fact_text (str): The fact text from which to extract keywords.

    Returns:
        list: A list of up to three keywords (strings).
    """
    # Define a basic set of stopwords.
    stopwords = {
        "the", "and", "a", "an", "of", "in", "to", "is", "are", "it", "that",
        "this", "with", "as", "for", "on", "by", "from", "at", "or", "be",
        "was", "were", "but", "not", "have", "has", "had", "you", "i"
    }
    # Remove punctuation and convert to lowercase.
    translator = str.maketrans("", "", string.punctuation)
    cleaned_text = fact_text.translate(translator).lower()
    
    words = cleaned_text.split()
    # Filter out common stopwords and very short words.
    keywords = [word for word in words if word not in stopwords and len(word) > 4]
    
    # Return unique keywords, preserving order; limit to three.
    seen = set()
    unique_keywords = []
    for word in keywords:
        if word not in seen:
            seen.add(word)
            unique_keywords.append(word)
        if len(unique_keywords) >= 3:
            break
    return unique_keywords