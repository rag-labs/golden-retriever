from fastapi import APIRouter, HTTPException
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from langchain_core.output_parsers import JsonOutputParser
import os
from dotenv import load_dotenv
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.base_parser import get_search_results

load_dotenv()

router = APIRouter()

# Define request model
class JsonFitterRequest(BaseModel):
    query: str
    json_schema: dict

llm = AzureChatOpenAI(deployment_name=os.getenv("MODEL_NAME"))
llm.bind(response_format={'type': 'json_object'})

# response_example = json.loads(open('backend/response_example.json', 'r').read())
# json_schema = json.loads(open('backend/response_schema.json', 'r').read())

def process_search_results(input_dict):
    """Convert search results into a detailed text description"""
    # Extract query from the input dictionary
    query = input_dict["query"]
    results = get_search_results(query)
    combined_text = []
    
    for i, result in enumerate(results, 1):
        section = [f"\nResult {i}:"]
        section.append(f"Title: {result.get('title', '')}")
        section.append(f"URL: {result.get('url', '')}")
        
        if result.get('meta_description'):
            section.append(f"Description: {result['meta_description']}")
        
        if result.get('images'):
            section.append("\nImages found:")
            for img in result['images'][:5]:  # Show first 5 images
                section.append(f"- {img['src']} ({img['alt']})")
        
        if result.get('summary'):
            section.append(f"\nContent Summary:\n{result['summary']}")
        elif result.get('main_text'):
            section.append(f"\nMain Content:\n{result['main_text'][:1000]}")  # First 1000 chars of main text
            
        combined_text.append("\n".join(section))
    
    # Return both restaurant_information and json_schema
    return {
        "restaurant_information": "\n" + "="*50 + "\n".join(combined_text),
        "json_schema": input_dict["json_schema"]  # Pass through the schema
    }

prompt = ChatPromptTemplate.from_template("""
You are a Golden Retriever. You are given a raw text response of information about a few restaurants.
Your job is to choose the restaurant which has the most data points that match the JSON schema provided.
And then fit that information into the JSON schema.
If there is not enough information to fill out the JSON schema, 
you should fill in the missing information with reasonable values that would make sense for a restaurant.

<restaurant_information>
{restaurant_information}
</restaurant_information>

<json_schema>
{json_schema}
</json_schema>

Always return a valid JSON object. Don't add any additional text or comments.
""")

parser = JsonOutputParser()

search_runnable = RunnableLambda(process_search_results)

chain = search_runnable | prompt | llm | parser

@router.post('/json_fitter')
async def json_fitter(request: JsonFitterRequest):
    try:
        result = chain.invoke({
            "query": request.query,
            "json_schema": request.json_schema
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))