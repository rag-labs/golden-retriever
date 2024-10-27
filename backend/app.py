from flask import Flask, request, jsonify
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Azure OpenAI
llm = AzureChatOpenAI(deployment_name=os.getenv("MODEL_NAME"))
# Placeholder for restaurant data
restaurant_data = [
    {
        "name": "Restaurant A",
        "description": "Cozy place with Italian cuisine",
        "feedback": ["Great pasta and friendly staff", "Excellent pizza and cozy atmosphere", "Staff is great, but the food is average"]
    },
    {
        "name": "Restaurant B",
        "description": "Modern ambiance with a variety of vegan options",
        "feedback": ["Loved the vegan burger and the decor", "The vegan options were delicious, but the service was slow", "The atmosphere was great, but the food was average"]
    },
    {
        "name": "Restaurant C",
        "description": "Authentic Japanese sushi restaurant",
        "feedback": ["Delicious sushi and friendly service", "Great food, and the service is incredbly fast", "Arguably the best service I've had, food is amazing as well!"]
    },
    {
        "name": "Restaurant D",
        "description": "High-end steakhouse with a modern twist",
        "feedback": ["Excellent steak and attentive staff", "The steak was cooked to perfection, and the service was excellent"]
    },
    {
        "name": "Restaurant E",
        "description": "Cozy coffee shop with a variety of pastries",
        "feedback": "Delicious coffee and cozy atmosphere"
    },
    {
        "name": "Restaurant F",
        "description": "Modern tapas bar with a vibrant atmosphere",
        "feedback": "Great tapas and lively atmosphere"
    },
    {
        "name": "Restaurant G",
        "description": "Authentic Mexican restaurant with a family-friendly vibe",
        "feedback": "Authentic Mexican food and friendly staff"
    },
    {
        "name": "Restaurant H",
        "description": "High-end French restaurant with a modern twist",
        "feedback": "Excellent French cuisine and elegant atmosphere"
    },
    {
        "name": "Restaurant I",
        "description": "Authentic Russian cuisine with a traditional atmosphere",
        "feedback": "Delicious Russian food and cozy atmosphere"
    },
]

# Initialize vector store and retriever
vectorstore = Chroma(embedding_function=AzureOpenAIEmbeddings(), persist_directory="./chroma_db_oai")
retriever = vectorstore.as_retriever(k=3)

# Define the prompt template
prompt_template = ChatPromptTemplate.from_template("""
Based on the user's preferences in cuisine, and the restaurant's description and feedback, answer the following questions:
1. What is the name of the restaurant?
2. Why is it a good match for the user's preferences?
3. What is the description of the restaurant?
<user_preferences>
{preferences}
</user_preferences>
<restaurant_description>
{description}
</restaurant_description>
<restaurant_feedback>
{feedback}
</restaurant_feedback>
""")


@app.route('/chat', methods=['POST'])
def chat():
    user_preferences = request.json.get('user_preferences')
    #Retrieve the top 3 restaurants that match the user's preferences
    restaurants = retriever.get_relevant_documents(user_preferences)
    #Return the restaurants to the user
    return jsonify(restaurants), 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)