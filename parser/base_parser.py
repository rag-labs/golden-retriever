import requests
from bs4 import BeautifulSoup
import re
import spacy
from transformers import pipeline, AutoTokenizer
import torch
from urllib.parse import urljoin
import json
from datetime import datetime

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize models
nlp = spacy.load('en_core_web_sm')
summarizer = pipeline('summarization', model='facebook/bart-large-cnn', device=device)
tokenizer = AutoTokenizer.from_pretrained('facebook/bart-large-cnn', device=device)

def search_duckduckgo(query):
    """
    Searches DuckDuckGo with the given query and returns a list of results with titles and links.
    """
    formatted_query = query.replace(' ', '+')
    url = f"https://duckduckgo.com/html/?q={formatted_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Referer": "https://duckduckgo.com/",
        "Accept-Language": "en-US,en;q=0.5"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for result in soup.find_all('a', {'class': 'result__a'}):
            title = result.text.strip()
            link = result['href']
            results.append({'title': title, 'link': link})
        return results
    else:
        return []
    
    
def scrape_page_content(url):
    """
    Retrieves comprehensive content from a given webpage including text, images, and metadata.
    Returns a dictionary containing structured page information.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Referer": url,
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize content dictionary
            content = {
                'url': url,
                'title': '',
                'meta_description': '',
                'main_text': '',
                'images': [],
                'timestamp': datetime.now().isoformat(),
            }
            
            # Extract title
            title_tag = soup.find('title')
            content['title'] = title_tag.text.strip() if title_tag else ''
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                content['meta_description'] = meta_desc.get('content', '')
            
            # Extract main text content
            paragraphs = soup.find_all('p')
            content['main_text'] = ' '.join([para.text.strip() for para in paragraphs])
            
            # Extract images with their alt text and source
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src and not src.startswith('data:'):  # Filter out data URLs
                    # Convert relative URLs to absolute URLs
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(url, src)
                    
                    # Only include images with valid http(s) URLs
                    if src.startswith(('http://', 'https://')):
                        image_info = {
                            'src': src,
                            'alt': img.get('alt', ''),
                            'title': img.get('title', '')
                        }
                        content['images'].append(image_info)
            
            return content
        else:
            return None
    
    except requests.exceptions.RequestException as e:
        return None


def clean_text(text):
    """
    Cleans the input text by removing unnecessary whitespace and special characters.
    """
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\[.*?\]', '', text)
    return text.strip()


def chunk_text(text, chunk_size=500):
    """
    Splits the input text into chunks of approximately `chunk_size` words.
    """
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def summarize_text(text, chunk_size=500):
    """
    Summarizes the input text in chunks to handle large inputs.
    Limits the final summary to approximately 20 sentences or 200 words.
    """
    # Step 1: Split text into chunks to fit within model's max length
    chunks = chunk_text(text, chunk_size=chunk_size)
    chunk_summaries = []
    
    # Step 2: Summarize each chunk individually
    for chunk in chunks:
        try:
            tokens = tokenizer(chunk, return_tensors="pt").input_ids
            input_length = len(tokens[0])

            # Dynamically set max_length and min_length for each chunk
            max_length = min(200, max(input_length // 2, 50))  
            min_length = min(max_length // 2, 30)              
            
            # Generate summary for the chunk
            summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
            chunk_summaries.append(summary[0]['summary_text'])
        
        except Exception as e:
            chunk_summaries.append(chunk)  # Fallback: use original chunk if summarization fails
    
    # Step 3: Combine summaries of chunks
    combined_summary = ' '.join(chunk_summaries)
    return combined_summary


def extract_keywords(text):
    """
    Extracts keywords from a given text using spaCy.
    """
    doc = nlp(text)
    keywords = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop and not token.is_punct]
    return list(set(keywords))

def get_search_results(query, top_results=5):
    """
    Performs a search and returns structured results for the top matches.
    
    Args:
        query (str): Search query
        top_results (int): Number of top results to return
        
    Returns:
        list: List of dictionaries containing structured content for each result
    """
    keywords = extract_keywords(query)
    clear_query = ' '.join(keywords)
    
    results = search_duckduckgo(clear_query)
    
    if not results:
        return []
    
    all_content = []
    for result in results[:top_results]:
        content = scrape_page_content(result['link'])
        if content:
            # Add the search result title and link
            content['search_title'] = result['title']
            content['search_link'] = result['link']
            
            # Generate summary
            if content['main_text']:
                content['summary'] = summarize_text(content['main_text'])
            else:
                content['summary'] = ''
                
            all_content.append(content)
    
    return all_content

def main():
    # Sample user query and keyword extraction
    user_query = "Find me restaurants in London where I can go with my family to eat Georgian cuisine"
    results = get_search_results(user_query, top_results=5)
    
    # Process and display the results
    for i, content in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Title: {content['title']}")
        print(f"URL: {content['url']}")
        print(f"Description: {content['meta_description'][:200]}...")
        
        # Display images
        if content['images']:
            print("\nImages found:")
            for img in content['images'][:5]:  # Show first 5 images
                print(f"- {img['src']} ({img['alt']})")
        
        # Display main content summary
        if content['summary']:
            print(f"\nSummary:\n{content['summary']}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    main()
