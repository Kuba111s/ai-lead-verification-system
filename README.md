# AI-Powered Lead Verification System
![image_thumbail2](https://github.com/user-attachments/assets/1be46dee-3e8a-463f-a2c6-5791420be4fb)

### The Business Problem
A client had a raw list of thousands of potential leads (URLs) but no way to know which ones were valid E-commerce stores and which were blogs, corporate sites, or dead links. Manually checking each site took ~2 minutes per URL.

### The Solution
I built a high-speed **Asynchronous Python Scraper** that acts as an intelligent filter. It visits websites in parallel, extracts page content, and uses **GPT-4o-mini** to analyze the business type, achieving **99% accuracy** in categorization.

### Key Features
* **Asynchronous Scraping:** Uses `Playwright` + `Asyncio` to load multiple sites simultaneously, significantly faster than synchronous requests.
* **AI Analysis:** Integrates `OpenAI API (GPT-4o-mini)` to "read" the website text and determine:
    * Is this an E-commerce store? (Yes/No)
    * What are the main products?
    * Why did you classify it this way? (Reasoning)
* **Smart JSON Parsing:** Includes robust error handling to strip Markdown formatting from AI responses and parse clean JSON data.
* **Automated Excel Reporting:** Uses `Pandas` and `XlsxWriter` to generate a client-ready report with:
    * Auto-adjusted column widths.
    * Formatted headers (Bold/Blue).
    * Built-in Excel filtering.

### Tech Stack
* **Python 3.9+**
* **Web Automation:** `playwright` (Headless Chromium)
* **AI Logic:** `openai`
* **Data Processing:** `pandas`, `json`
* **Reporting:** `xlsxwriter`
