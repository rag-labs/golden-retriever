from flask import Flask, request, jsonify
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)

llm = AzureChatOpenAI(deployment_name=os.getenv("MODEL_NAME"))

response_example = json.loads(open('response_example.json', 'r').read())
#Get the JSON schema from the response example
json_schema = json.loads(open('response_schema.json', 'r').read())
prompt = ChatPromptTemplate.from_template("""
You are a JSON fitter. You are given a raw text response of information about a restaurant. Your job is to fit that information into the JSON schema provided.
If there is not enough information to fill out the JSON schema, you should fill in the missing information with reasonable values that would make sense for a restaurant.

<restaurant_information>
{restaurant_information}
</restaurant_information>

<json_schema>
{json_schema}
</json_schema>
""")

