# Web Agent: Automating Browser Tasks with AI

**Web Agent** is a cutting-edge AI-powered system designed to automate web browsing tasks. It leverages the **Playwright** framework to control browsers and an LLM (Large Language Model) for decision-making. The agent identifies interactive elements on a webpage and performs actions to complete user-defined tasks efficiently.

## Demo
https://github.com/user-attachments/assets/b8079314-d4d6-4ec2-a1f3-da5c1269f810

---

Here’s the updated version of the project description, incorporating the changes you've mentioned:  

---

## Key Features  

- **Interactive Element Detection:**  
  The agent automatically detects and highlights interactive components like buttons, input fields, and links on a webpage. It does this by analyzing **screenshots** to identify these elements and overlaying **bounding boxes** for precise targeting. Additionally, it captures the **current state of the browser**, enhancing the accuracy of context-aware actions.

- **Accessibility Tree Integration:**  
  While primarily leveraging screenshots and browser state for interaction, the agent retains its ability to utilize the **accessibility tree**. This allows for efficient performance in resource-constrained environments and enables seamless interaction without relying on visual data alone.  

- **LLM-Based Decision Making:**  
  Powered by advanced **Large Language Models (LLMs)**, the agent uses contextual reasoning to determine the appropriate actions to take. It leverages the following state-of-the-art LLMs:  
  - **Groq:** llama-3.3-70b-versatile  
  - **Gemini:** gemini-1.5-flash/gemini-2.0-flash-exp 

  These models enable intelligent decision-making by processing screenshots, browser states, or accessibility trees to understand the task and webpage context.  

- **Error Handling and Recovery:**  
  The agent intelligently recovers from incorrect actions, such as misclicks or missed interactions. It adapts to frequent layout changes, ensuring reliable performance in dynamic environments.  

- **Cross-Browser Compatibility:**  
  The system supports multiple browser engines, including **Chromium**, **Firefox**, and **WebKit (Safari)**, by utilizing **Playwright’s cross-browser capabilities**. This ensures compatibility across diverse platforms and environments. 

---

## How It Works  

1. **Screenshot, Annotation, and State Capture:**  
   The agent takes a **screenshot** of the web page, highlights interactive elements using **bounding boxes**, and captures the **current state of the browser** (including DOM structure, scroll position, and other key data).  

2. **Data Processing and Action Assignment:**  
   The LLM processes the visual data (screenshots), browser state, and other context to assign the correct action (e.g., click, type, scroll) to the corresponding interactive element.  

3. **Interaction Execution:**  
   The agent performs the instructed action on the identified element.  

4. **Result Evaluation and Adaptation:**  
   After executing an action, the agent evaluates the result and adjusts its strategy if the desired outcome isn't achieved.  

---

## Example

### Task: Download a Research Paper

```plaintext
python main.py "Download the attention paper from google search"                          
Thought: I need to search for the attention paper on google and then download it. I will start by going to google.com.
Action Name: GoTo Tool
Action Input: {'url': 'https://www.google.com'}
Observation: Navigated to https://www.google.com
Thought: I need to type "attention paper" in the search box. The search box has index 6.
Action Name: Type Tool
Action Input: {'index': 6, 'text': 'attention paper'}
Observation: Clicked element 33
Thought: I see a link with the text "Attention is All You Need" and a pdf icon next to it. This is likely the paper I need to download. The link has index 48.
Action Name: Click Tool
Action Input: {'index': 48}
Observation: Clicked element 48
Thought: I have navigated to the pdf of the attention paper. Now I need to download it. I will use the Download Tool and provide the current url and a filename.
Action Name: Download Tool
Action Input: {'url': 'https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf', 'filename': 'attention_paper.pdf'}
Observation: Downloaded attention_paper.pdf from https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf
Thought: I have downloaded the attention paper. I am done with the task.
Final Answer: I have downloaded the attention paper successfully.
I have downloaded the attention paper successfully.
```
---

## Installation

### Prerequisites

- Python 3.8+
- Playwright installed on your system

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/Jeomon/Web-Agent.git
   cd Web-Agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Playwright:
   ```bash
   playwright install
   ```

---

## Usage

Start the Web Agent with the following command:

```bash
python main.py "Your query goes here"
```

---

Feel free to customize further or share feedback!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

- **Playwright Documentation:** [https://playwright.dev/docs/intro](https://playwright.dev/docs/intro)
- **WebVoyager:** [https://github.com/MinorJerry/WebVoyager](https://github.com/MinorJerry/WebVoyager)
- **Langgraph Examples:** [https://github.com/langchain-ai/langgraph/blob/main/examples/web-navigation/web_voyager.ipynb](https://github.com/langchain-ai/langgraph/blob/main/examples/web-navigation/web_voyager.ipynb)
- **vimGPT:** [https://github.com/ishan0102/vimGPT](https://github.com/ishan0102/vimGPT)
- **browser-use:** [https://github.com/browser-use/browser-use](https://github.com/browser-use/browser-use)

---