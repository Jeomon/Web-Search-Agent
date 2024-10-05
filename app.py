from src.inference.gemini import ChatGemini
from src.agent.web import WebSearchAgent
from src.message import HumanMessage,SystemMessage
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
api_key=os.getenv('GOOGLE_API_KEY')

llm=ChatGemini(model='gemini-1.5-flash',api_key=api_key,temperature=0)