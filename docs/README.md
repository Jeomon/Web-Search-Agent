# **Web Agent: Automating Browser Tasks with AI**

## Overview
**Web Agent** is a state-of-the-art browser automation tool driven by advanced AI technologies. Designed for seamless navigation and task execution on the web, it intelligently interacts with dynamic web elements, performs searches, downloads files, and adapts to page changes. By leveraging cutting-edge LLMs and the Playwright framework, Web Agent simplifies complex tasks and enhances productivity.

## Demo
https://github.com/user-attachments/assets/499f248c-b160-45cc-a6a5-2819b6955aab

---

## **Key Features**

1. **AI-Driven Decision Making**  
   - Utilizes **Groq (Llama 3.3)** and **Gemini (Gemini 2.0)** LLMs for contextual understanding and task execution.
   - Smart reasoning ensures the correct action is taken based on webpage context.

2. **Interactive Element Detection**  
   - Automatically identifies clickable elements, input fields, and navigation links.
   - Utilizes screenshots, bounding boxes, and browser state capture for precise targeting.

3. **Multi-Browser Compatibility**  
   - Supports **Chromium**, **Firefox**, and **WebKit (Safari)** via Playwright for cross-platform performance.

4. **Dynamic Adaptation**  
   - Handles dynamic content changes and page layout variations.
   - Automatically recovers from errors such as misclicks or missed interactions.

5. **Enhanced Performance Options**  
   - Supports both **visual-based** interactions through screenshots and **non-visual** interactions using accessibility trees for resource-efficient automation.

---

## **How It Works**

1. **State Capture & Interaction Analysis:**  
   - Captures browser state and webpage layout, annotates interactive elements, and stores relevant data for decision-making.

2. **LLM Integration:**  
   - Processes contextual data to determine the best action for completing tasks.
   
3. **Action Execution:**  
   - Automates task execution such as navigating pages, filling forms, and downloading content.

4. **Feedback Loop:**  
   - Evaluates outcomes and refines strategy for subsequent actions.

---

## **Usage Example**

### **Task: Download a Research Paper**

```bash
python main.py "Can you download the attention is all you need paper in ARXIV from google search"
```

#### Example Output:

```plaintext
Enter your query: Can you download the attention is all you need paper in ARXIV from google search
Thought: I need to search for the "attention is all you need" paper on Google and then navigate to the arXiv link to download the PDF. I will start by going to google.com.
Action Name: GoTo Tool
Action Input: {'url': 'https://www.google.com'}
Observation: Navigated to https://www.google.com
Thought: I need to type "attention is all you need paper arxiv" in the search box. The search box has index 6.
Action Name: Type Tool
Action Input: {'index': 6, 'text': 'attention is all you need paper arxiv'}
Observation: Typed attention is all you need paper arxiv in element 6
Thought: Now I need to click the Google Search button to search for the paper. The Google Search button has index 13.
Action Name: Click Tool
Action Input: {'index': 13}
Observation: Clicked element 13
Thought: I see a link to the PDF of the paper on arxiv with index 25. I will click on that to download the paper.
Action Name: Click Tool
the url directly. I will use the download tool with the current url and a filename.
Action Name: Download Tool
Action Input: {'url': 'http://arxiv.org/pdf/1706.03762', 'filename': 'attention_is_all_you_need.pdf', 'index': 0}
Observation: Downloaded attention_is_all_you_need.pdf from http://arxiv.org/pdf/1706.03762 and saved it to .\downloads\attention_is_all_you_need.pdf
Thought: I have successfully downloaded the paper. I can now provide the final answer.
Final Answer: I have downloaded the "attention is all you need" paper from arXiv. The file is saved as attention_is_all_you_need.pdf.
I have downloaded the "attention is all you need" paper from arXiv. The file is saved as attention_is_all_you_need.pdf.
```

---

## **Installation Guide**

### **Prerequisites**

- Python 3.8 or higher
- Playwright installed

### **Installation Steps**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Jeomon/Web-Agent.git
   cd Web-Agent
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Playwright:**

   ```bash
   playwright install
   ```

---

## **Running the Web Agent**

Execute the following command to start the agent:

```bash
python main.py "Describe your task here"
```

Example:  
```bash
python main.py "Find and download the latest AI white paper."
```

---

## **Advanced Usage**

- **Enable Debugging:** Set `verbose=True` in the agent configuration for detailed logs.
- **Custom Instructions:** Modify task-specific instructions for custom workflows.

---

## **Development & Contributions**

We welcome contributions to improve Web Agent! Please feel free to fork the repository, submit issues, or create pull requests.

### **Project Structure**

- **src/agent:** Core logic and automation tools.
- **src/inference:** LLM integration and reasoning functions.
- **src/browser:** Browser configuration and session handling.
- **examples:** Sample tasks and demonstrations.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **References**

- **[Playwright Documentation](https://playwright.dev/docs/intro)**  
- **[LangGraph Examples](https://github.com/langchain-ai/langgraph/blob/main/examples/web-navigation/web_voyager.ipynb)**  
- **[vimGPT](https://github.com/ishan0102/vimGPT)**  
- **[WebVoyager](https://github.com/MinorJerry/WebVoyager)**  

---

## **Contact**

For queries or support, please reach out via GitHub Issues.

---

This updated `README.md` incorporates key details about the system while providing clearer instructions and an enhanced user experience. Would you like additional customization or features added?