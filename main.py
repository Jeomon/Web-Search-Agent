import argparse
from src.inference.gemini import ChatGemini
from src.agent.web import WebAgent
from dotenv import load_dotenv
import os

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set in the .env file.")

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the Web Agent to solve the query.")
    parser.add_argument('query', type=str, help="The query you want the Web Agent to process.")
    args = parser.parse_args()
    
    # Initialize LLM and Web Agent
    llm = ChatGemini(model='gemini-2.0-flash-exp', api_key=api_key, temperature=0)
    agent = WebAgent(instructions=[],llm=llm, browser='chromium', verbose=True, headless=False, use_vision=True)
    
    # Invoke the agent with the user's query
    user_query = args.query
    agent_response = agent.invoke(user_query)
    print(agent_response)

if __name__ == "__main__":
    main()
