from src.embedding.gemini import GeminiEmbedding
from src.inference.gemini import ChatGemini
from src.agent.web import WebSearchAgent
from dotenv import load_dotenv
import os

load_dotenv()
api_key=os.getenv('GOOGLE_API_KEY')
llm=ChatGemini(model='gemini-1.5-flash',api_key=api_key,temperature=0)
embedding=GeminiEmbedding(model='text-embedding-004',api_key=api_key)

agent=WebSearchAgent(llm=llm,embedding=embedding,browser='edge',verbose=True,strategy='screenshot',headless=False,incognito=True,screenshot=True)
user_query=input('Enter your query: ')
agent_response=agent.invoke(user_query)
print(agent_response)