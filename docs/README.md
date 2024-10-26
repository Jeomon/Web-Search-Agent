# Web Search Agent

**Web Search Agent** is an intelligent system built with **Playwright** to automate web browsing tasks. This agent interacts with web pages by identifying and acting on interactive elements, such as buttons, links, and input fields. It now supports two modes of operation: using annotated screenshots with bounding boxes and utilizing the accessibility (a11y) tree, allowing for a more efficient web search experience without the need for visual processing. 

## Demo
https://github.com/user-attachments/assets/b8079314-d4d6-4ec2-a1f3-da5c1269f810

## Key Features

- **Interactive Element Detection:** The agent automatically detects and highlights interactive components like buttons, input fields, and links on a webpage, regardless of the method used (screenshot or a11y tree).

- **Dynamic Action Execution:** The agent executes a wide range of actions, including:
  - **Clicking** on buttons or links.
  - **Typing** into input fields.
  - **Scrolling** through web pages.
  - **Waiting** for content to load.
  - **Navigating** between web pages.
  It adapts its actions based on instructions and can execute the right task on the corresponding interactive element.

- **Accessibility Tree Integration:** With the newly added capability to utilize the accessibility tree, the agent can perform web searches without taking a screenshot. This allows for enhanced performance and reduced resource usage, making it suitable for a wider range of environments.

- **LLM-Based Decision Making:** Powered by a **Large Language Model (LLM)**, the agent analyzes the context of the web page and makes intelligent decisions on which actions to take, whether using the screenshot or a11y tree method.

- **Error Handling and Recovery:** The agent is capable of recovering from incorrect actions, such as clicking on the wrong element or missing interactions. It ensures precise actions even on pages with frequent layout changes.

- **Cross-Browser Compatibility:** The system works with multiple browser engines, including **Chromium**, **Firefox**, and **WebKit (Safari)**, thanks to Playwright’s cross-browser support. This ensures the agent can operate across a wide variety of platforms and environments.

- **Handling Dynamic Content:** The agent waits for all dynamic content to load before interacting, improving reliability on pages with delayed or asynchronous content loading.

## How It Works

1. **Screenshot & Annotation or A11y Tree Analysis:** The agent can either take a screenshot of the web page and label interactive elements with **bounding boxes** or analyze the accessibility tree to identify interactive components.

2. **Action Assignment:** The LLM processes the data (from either method) to identify which action (e.g., click, type, scroll) to perform based on the task.

3. **Interaction Execution:** The agent performs the instructed action on the correct interactive element.

4. **Result Evaluation:** After executing the action, the agent evaluates the result and adjusts its next steps, if necessary.

### Example Queries

#### Example: Find the distance between two places from Google Maps using screenshot

```plaintext
Enter your query: Can you tell me the distance from Kochi to Singapore?
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

#### Example: Weather of a place using a11y tree

```plaintext
Enter your query: What is the weather in singapore
Thought: I need to navigate to a search engine to find the answer to the user's query about the weather in Singapore.
Action Name: GoTo Tool
Action Input: {'url': 'https://www.google.com'}
Observation: Gone to https://www.google.com.
Thought: I should use the Type Tool to enter the user's query, "weather in singapore", into the search bar, which has the role 'combobox' and name 'Search'.
Action Name: Type Tool
Action Input: {'role': 'combobox', 'name': 'Search', 'content': 'weather in singapore'}
Observation: Typed weather in singapore.
Thought: The A11y Tree contains the answer to the user's query. I can see the weather information for Singapore, including temperature, precipitation, humidity, and wind.
Final Answer: The weather in Singapore is mostly cloudy with a temperature of 30°Celsius. There is a 2% chance of precipitation, 67% humidity, and a wind speed of 10 km/h.
The weather in Singapore is mostly cloudy with a temperature of 30°Celsius. There is a 2% chance of precipitation, 67% humidity, and a wind speed of 10 km/h.
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

Once installed, you can choose between using the screenshot method or the accessibility tree method. The agent can be executed with the following command:

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

---