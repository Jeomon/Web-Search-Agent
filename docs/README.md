# Web Agent: Automating Browser Tasks with AI

**Web Agent** is a cutting-edge AI-powered system designed to automate web browsing tasks. It leverages the **Playwright** framework to control browsers and an LLM (Large Language Model) for decision-making. The agent identifies interactive elements on a webpage and performs actions to complete user-defined tasks efficiently.

## Demo
https://github.com/user-attachments/assets/b8079314-d4d6-4ec2-a1f3-da5c1269f810

---

## Key Features

1. **Automated Task Execution**: 
   - Capable of automating web searches and interactions.
   - Executes actions like clicking buttons, filling forms, and navigating pages.

2. **Interactive Element Detection**: 
   - Uses Playwright's **accessibility tree (a11y tree)** to locate interactive elements on web pages.
   - Highlights elements and interacts with them based on LLM-generated decisions.

3. **Bounding Box Integration**: 
   - Captures a screenshot of the webpage.
   - Draws bounding boxes around interactive elements for LLM-based contextual analysis.

4. **LLM-Driven Workflow**: 
   - Analyzes webpage structure and task objectives using advanced AI models.
   - Determines and executes the next action in a step-by-step manner.

5. **Browser Compatibility**: 
   - Works across major browsers like **Chromium**, **Firefox**, and **WebKit** using Playwright.

6. **Dynamic Adaptability**: 
   - Handles complex, dynamic web pages with asynchronous content loading.
   - Adapts actions based on real-time feedback and page changes.

---

## Example Workflow

### Task: Download a Research Paper

```plaintext
Enter your query: Download the attention paper from google search                             
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

---

## Installation

### Prerequisites

- Python 3.8+
- Playwright installed on your system

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/Jeomon/web-agent.git
   cd web-agent
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
python main.py
```

---

## Contributing

We welcome contributions to improve the Web Agent! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

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