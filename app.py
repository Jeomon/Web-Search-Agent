from src.inference.gemini import ChatGemini
from src.agent.web import WebAgent
from dotenv import load_dotenv
import os

load_dotenv()
api_key=os.getenv('GOOGLE_API_KEY')
llm=ChatGemini(model='gemini-1.5-flash',api_key=api_key,temperature=0)

agent = WebAgent(instructions=[],llm=llm, browser='edge', verbose=True, headless=False, use_vision=True)
user_query=input('Enter your query: ')
agent_response=agent.invoke(user_query)
print(agent_response)