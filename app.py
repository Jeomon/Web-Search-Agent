from src.inference.gemini import ChatGemini
from src.inference.groq import AudioGroq
from src.agent.web import WebAgent
from src.speech import Speech
from dotenv import load_dotenv
import os

load_dotenv()
google_api_key=os.getenv('GOOGLE_API_KEY')
groq_api_key=os.getenv('GROQ_API_KEY')
llm=ChatGemini(model='gemini-2.0-flash-exp',api_key=google_api_key,temperature=0)
audio_llm=AudioGroq(model='whisper-large-v3',mode='translations',api_key=groq_api_key,temperature=0)

agent = WebAgent(instructions=[],llm=llm, browser='edge', verbose=True, headless=False, use_vision=False)
mode=input('Enter the mode of input (text/voice): ')
if mode=='text':
    user_query=input('Enter your query: ')
elif mode=='voice':
    speech=Speech(llm=audio_llm)
    user_query=speech.invoke()
    print(f'Enter your query: {user_query.content}')
else:
    raise Exception('Invalid mode of input. Please enter either text or voice.')
agent_response=agent.invoke(user_query)
print(agent_response)
