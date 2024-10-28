import requests
from bs4 import BeautifulSoup
import re
import spacy
from transformers import pipeline, AutoTokenizer


# Initialize models
nlp = spacy.load('en_core_web_sm')
summarizer = pipeline('summarization', model='facebook/bart-large-cnn')
tokenizer = AutoTokenizer.from_pretrained('facebook/bart-large-cnn')


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
    Retrieves the textual content from a given webpage.
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
            paragraphs = soup.find_all('p')
            return ' '.join([para.text for para in paragraphs])
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


def main():
    # Sample user query and keyword extraction
    user_query = "Find me restaurants in London where I can go with my family to eat Sushi or other asian cuisine"
    keywords = extract_keywords(user_query)
    clear_query = ' '.join(keywords)
    print(f"Generated Search Query: {clear_query}")

    # Search using the clear query and scrape results
    results = search_duckduckgo(clear_query)

    if results:
        scraped_contents = []
        for result in results:
            content = scrape_page_content(result['link'])
            if content:
                cleaned_content = clean_text(content)
                scraped_contents.append(cleaned_content)
        
        # Summarize each scraped content using the chunked summarization
        summaries = [summarize_text(content) for content in scraped_contents]

        # Print each summary
        for i, summary in enumerate(summaries):
            print(f"Summary {i + 1}:\n{summary}\n")
    else:
        print("No results found.")


if __name__ == "__main__":
    main()
