import requests
from bs4 import BeautifulSoup
import re
import transformers
from transformers import pipeline, AutoTokenizer

def search_duckduckgo(query):
    query = query.replace(' ', '+')
    url = f"https://duckduckgo.com/html/?q={query}"
    
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
            results.append({
                'title': title,
                'link': link,
            })
        return results
    else:
        print(f"Failed to retrieve search results: {response.status_code}")
        return []

def scrape_page_content(url, proxies=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Referer": url,
        "Accept-Language": "en-US,en;q=0.5"
    }
    response = requests.get(url, headers=headers, proxies=proxies)
    print(response)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        page_text = ' '.join([para.text for para in paragraphs])
        return page_text
    else:
        print(f"Failed to retrieve page content: {response.status_code}")
        return None
    
def clean_text(text):
    cleaned_text = re.sub(r'\s+', ' ', text)
    clean_text = re.sub(r'\[.*?\]', '', cleaned_text)
    clean_text = cleaned_text.strip()
    return cleaned_text    
    
query = "asian cafe Moscow"
result = search_duckduckgo(query)
links = [r['link'] for r in result]
    
    
scraped_content = []
for link in links:
    content = scrape_page_content(link)
    if content:
        scraped_content.append(content)
        
cleaned_content = [clean_text(content) for content in scraped_content]

summarizer = pipeline('summarization', model='facebook/bart-large-cnn')
tokenizer = AutoTokenizer.from_pretrained('facebook/bart-large-cnn')

def summarize_text(text):
    # Tokenize the text and get the number of tokens
    tokens = tokenizer(text, return_tensors="pt").input_ids
    # print(tokens)
    
    # Check if the number of tokens exceeds the model's maximum input length
    max_token_length = tokenizer.model_max_length
    input_length = len(tokens[0])
    # print(input_length, max_token_length)
    
    if input_length > max_token_length:
        print(f"Input too long: {input_length} tokens (max: {max_token_length}), truncating...")
        text = tokenizer.decode(tokens[0][:max_token_length], skip_special_tokens=True)
        # print("Truncated text:", text)
    
    try:
        # Set max_length dynamically based on input length
        max_length = min(input_length // 2, 150)
        min_length = min(input_length // 4, 30)
        
        if input_length < 10:
            return text  # Skip summarization if input is too short
        # print(max_length, min_length)

        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        # print(summary)
        return summary[0]['summary_text']
    
    except Exception as e:
        print(f"Error during summarization: {e}")
        return text

query = "restaurants asian cusine new york"
results = search_duckduckgo(query)

if results:
    scraped_contents = []
    for result in results:
        content = scrape_page_content(result['link'])  
        if content:
            cleaned_content = clean_text(content)
            scraped_contents.append(cleaned_content)
    
    summaries = [summarize_text(content) for content in scraped_contents]

    for i, summary in enumerate(summaries):
        print(f"Summary {i+1}:\n{summary}\n")
else:
    print("No results found.")




