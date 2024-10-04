# Web Search Agent

**Web Search Agent** is an intelligent system built with **Playwright** to automate web browsing tasks. This agent interacts with web pages by identifying and acting on interactive elements, such as buttons, links, and input fields, using annotated screenshots. It efficiently performs complex web interactions through precise actions and context-based decision-making, offering a robust solution for web automation, testing, and intelligent browsing.

[Demo of the Project](https://github.com/Jeomon/Web-Search-Agent/blob/main/assets/)

## Key Features

- **Interactive Element Detection:** The agent automatically detects and highlights interactive components like buttons, input fields, and links on a webpage. Each element is uniquely labeled with **bounding boxes** for clear reference, enabling the agent to perform the correct actions with precision.

- **Dynamic Action Execution:** The agent executes a wide range of actions, including:
  - **Clicking** on buttons or links.
  - **Typing** into input fields.
  - **Scrolling** through web pages.
  - **Waiting** for content to load.
  - **Navigating** between web pages.
  It adapts its actions based on instructions and can execute the right task on the corresponding interactive element.

- **LLM-Based Decision Making:** Powered by a **Large Language Model (LLM)**, the agent analyzes the context of the web page and makes intelligent decisions on which actions to take. This makes it highly adaptive, allowing it to handle complex interactions that depend on the web page’s content.

- **Error Handling and Recovery:** The agent is capable of recovering from incorrect actions, such as clicking on the wrong element or missing interactions. By using coordinate-based labeling and dynamic screenshots, the agent ensures precise actions, even on pages with frequent layout changes.

- **Cross-Browser Compatibility:** The system works with multiple browser engines, including **Chromium**, **Firefox**, and **WebKit (Safari)**, thanks to Playwright’s cross-browser support. This ensures the agent can operate across a wide variety of platforms and environments.

- **Handling Dynamic Content:** The agent waits for all dynamic content to load before interacting, improving reliability on pages with delayed or asynchronous content loading.

## How It Works

1. **Screenshot & Annotation:** The agent takes a screenshot of the web page and labels interactive elements with **bounding boxes** and unique numbers.
   
2. **Action Assignment:** The LLM processes the annotated screenshot, identifying which action (e.g., click, type, scroll) to perform based on the task.

3. **Interaction Execution:** The agent performs the instructed action on the correct interactive element.

4. **Result Evaluation:** After executing the action, the agent evaluates the result and adjusts its next steps, if necessary.

### Example Queries

#### Example: Find the distance between two places using Google Maps

```plaintext
Enter your query: Can you tell me the distance from kochi to singapore.
Thought: I will navigate to Google Maps to find the distance between Kochi and Singapore.
Observation: Typed Singapore.
Thought: I will click on the "Directions" button to get the distance between Kochi and Singapore.
Action Name: Click Tool
Action Input: {'label_number': 17}
Observation: Clicked the Button.
Thought: I will type "Kochi" in the "Choose starting point, or click on the map" field to find the distance between Kochi and Singapore.
Action Name: Type Tool
Action Input: {'label_number': 9, 'content': 'Kochi'}
Observation: Typed Kochi.
Thought: The screenshot shows the distance between Kochi and Singapore is 4 hours and 40 minutes by flight.
Final Answer: The distance from Kochi to Singapore is 4 hours and 40 minutes by flight.
```

## Installation

To set up the Web Search Agent, follow these steps:

1. Install Python 3.x and ensure it’s available in your environment.
2. Install project dependencies by running:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up **Playwright**:

   ```bash
   playwright install
   ```

## Usage

Once installed, the agent can be executed with the following command:

```bash
python app.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

- **Playwright Documentation:** [https://playwright.dev/docs/intro](https://playwright.dev/docs/intro)
- **WebVoyager:** [https://github.com/MinorJerry/WebVoyager](https://github.com/MinorJerry/WebVoyager)
- **Langgraph Examples:** [https://github.com/langchain-ai/langgraph/blob/main/examples/web-navigation/web_voyager.ipynb](https://github.com/langchain-ai/langgraph/blob/main/examples/web-navigation/web_voyager.ipynb)
- **vimGPT:** [https://github.com/ishan0102/vimGPT](https://github.com/ishan0102/vimGPT)