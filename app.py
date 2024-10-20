from src.inference.gemini import ChatGemini
from src.agent.web import WebSearchAgent
from dotenv import load_dotenv
import os

load_dotenv()
api_key=os.getenv('GOOGLE_API_KEY')

llm=ChatGemini(model='gemini-1.5-pro',api_key=api_key,temperature=0)
agent=WebSearchAgent(llm=llm,browser='edge',verbose=True,strategy='ally_tree',headless=False)
user_query=input('Enter your query: ')
agent_response=agent.invoke(user_query)
print(agent_response)