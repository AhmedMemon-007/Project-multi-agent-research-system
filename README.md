# Multi-Agent Research System

A research assistant built with **LangChain** that turns a topic into a structured report. Two tool-using agents and two LLM chains work in sequence: they search the web, read the most relevant source, write a report, and then review it.

**Live demo:** [ahmed-multi-agent-research.streamlit.app](https://ahmed-multi-agent-research.streamlit.app/)
---

## Table of Contents
1. [How It Works](#how-it-works)
2. [Agents and Chains](#agents-and-chains)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Setup](#setup)
6. [Usage](#usage)
7. [Example Output](#example-output)
8. [Limitations and Possible Solutions](#limitations-and-possible-solutions)
9. [Future Work](#future-work)

---

## How It Works

```
          Topic
            │
            ▼
┌───────────────────────┐   web_search (Tavily)
│  1. Search Agent      │ ─────────────────────▶  titles, URLs, snippets
└───────────────────────┘
            │
            ▼
┌───────────────────────┐   scrape_url (Requests + BeautifulSoup)
│  2. Reader Agent      │ ─────────────────────▶  full text of the best URL
└───────────────────────┘
            │
            ▼
┌───────────────────────┐
│  3. Writer Chain      │ ─────────────────────▶  structured research report
└───────────────────────┘
            │
            ▼
┌───────────────────────┐
│  4. Critic Chain      │ ─────────────────────▶  score, strengths, improvements
└───────────────────────┘
```

All results are stored in one shared `state` dictionary, which is passed from one step to the next.

## Agents and Chains

The system uses two different LangChain patterns:
- **Agents** are used where the LLM must **decide which action to take** (which search to run, which URL to read).
- **Chains** are used where the task is **fixed** (write a report, review a report). They are simpler, faster and more predictable.

| Step | Type | Tool | What it does |
|---|---|---|---|
| **Search Agent** | Agent (`create_agent`) | `web_search` | Searches the web with Tavily and returns the top 5 results (title, URL, 300-character snippet). |
| **Reader Agent** | Agent (`create_agent`) | `scrape_url` | Picks the most relevant URL from the search results, then scrapes and cleans its text (up to 3,000 characters). |
| **Writer Chain** | Chain (`prompt \| llm \| parser`) | none | Combines the search results and scraped content into a report: Introduction, Key Findings, Conclusion, Sources. |
| **Critic Chain** | Chain (`prompt \| llm \| parser`) | none | Reviews the report and returns a score out of 10, strengths, areas to improve and a one-line verdict. |

### LangChain features used
- `create_agent`: tool-calling agents
- `@tool`: turns Python functions into tools the agent can call
- `ChatGoogleGenerativeAI`: Gemini model wrapper
- `ChatPromptTemplate`: reusable system and human prompts
- LCEL (`|` pipe syntax) with `StrOutputParser`: simple prompt → model → text chains

## Tech Stack

| Area | Tools |
|---|---|
| Agent framework | LangChain |
| LLM | Google Gemini (`gemini-3.5-flash-lite`) |
| Web search | Tavily API |
| Web scraping | Requests, BeautifulSoup |
| Interface | Streamlit (web app), Rich (terminal output) |
| Configuration | python-dotenv |

## Project Structure

```
multi-agent-research-system/
├── app.py            # Streamlit web interface
├── pipeline.py       # Command-line version of the pipeline
├── agents.py         # LLM setup, search/reader agents, writer/critic chains
├── tools.py          # web_search and scrape_url tools
├── requirements.txt  # Python dependencies
├── .env              # API keys (not uploaded to GitHub)
└── README.md
```

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/AhmedMemon-007/Project-multi-agent-research-system.git
cd Project-multi-agent-research-system
```

### 2. Create a virtual environment
```bash
python -m venv myenv
myenv\Scripts\activate        # Windows
# source myenv/bin/activate   # macOS / Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
langchain
langchain-core
langchain-google-genai
tavily-python
requests
beautifulsoup4
python-dotenv
rich
streamlit
```

### 4. Add your API keys
Create a file named `.env` in the project folder:
```
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```
- Gemini key: [Google AI Studio](https://aistudio.google.com/apikey)
- Tavily key: [tavily.com](https://tavily.com)

> Never upload `.env` to GitHub. Add it to `.gitignore`.

## Usage

**Web app:**
```bash
streamlit run app.py
```
Enter a topic and select **Run Research**. The app shows live progress for each step and puts the results in three tabs: **Report**, **Critic Review** and **Raw Data**.

**Command line:**
```bash
python pipeline.py
```
Enter a topic when asked. Each step's output is printed in the terminal.

## Example Output

**Topic:** _Impact of war on the stock market_

**Report (shortened):**
```
Introduction
...
Key Findings
1. ...
2. ...
3. ...
Conclusion
...
Sources
- https://...
```

**Critic review (shortened):**
```
Score: 8/10
Strengths:
- ...
Areas to Improve:
- ...
One line verdict:
...
```

_Replace with a real example from your own run._

## Limitations and Possible Solutions

### 1. Only one source is read in depth
**Problem:** the Reader Agent scrapes a single URL. The report depends heavily on that one page, and the other results are only seen as short snippets.

**Possible solution:** let the Reader Agent scrape the top 2–3 URLs, or run several scrapes in parallel and merge the results.

### 2. Scraped text is cut to 3,000 characters
**Problem:** long articles are cut short, so important details further down the page may be missed.

**Possible solution:** raise the limit, or split long pages into chunks and summarize each chunk before passing it to the writer.

### 3. Reader Agent only sees the first 800 characters of search results
**Problem:** the search output is cut to 800 characters to keep the prompt small. URLs from results further down the list may never be considered.

**Possible solution:** pass only the titles and URLs (without snippets) to the Reader Agent. This is short enough to include all five results.

### 4. Some websites cannot be scraped
**Problem:** pages that load content with JavaScript, need a login, or block bots return little or no text.

**Possible solution:** fall back to the next search result when scraping fails, or use Tavily's built-in content extraction.

### 5. The critic's feedback is not used
**Problem:** the Critic Chain reviews the report, but the report is never improved based on that feedback. The pipeline runs in one direction only.

**Possible solution:** add a revision loop. If the score is below a threshold, send the feedback back to the Writer Chain for a second draft. **LangGraph** is well suited for this kind of loop.

### 6. No check that the facts and sources are correct
**Problem:** the LLM may misstate facts or list sources that do not support a claim. The critic judges writing quality, not factual accuracy.

**Possible solution:** ask the writer to cite a source next to each finding, and add a fact-check step that compares claims against the scraped text.

### 7. API rate limits
**Problem:** the Gemini free tier allows a limited number of requests per minute. One run makes several LLM calls in a row, which can lead to "429 Too Many Requests" errors.

**Possible solution:** keep `max_retries` enabled (already set), add LangChain's `InMemoryRateLimiter`, or use a paid API key.

### 8. Duplicate pipeline logic
**Problem:** the same pipeline steps are written twice, once in `pipeline.py` and once in `app.py`. A change in one file must be copied to the other.

**Possible solution:** move each step into a shared function that both files call.

## Future Work
- Add a **writer–critic revision loop** with LangGraph.
- Read **multiple sources** and compare them.
- Let users **download the report** as Markdown or PDF.
- Add **conversation memory**, so users can ask follow-up questions about the report.
- Show **token usage and run time** for each step.

## Author
**Muhammad Ahmed Memon**
