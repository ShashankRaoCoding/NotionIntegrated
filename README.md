
# Notion Integrated LinkedIn Post Generator

This project connects Notion with Ollama/Claude to generate LinkedIn posts using advanced language models.

---

## Dependencies

### Ollama  
- [Ollama](https://ollama.com/) — Required for running and interacting with the LLM locally.  
- Claude API key if you are using the Claude integration.

### Python Packages  
- `ollama` (Python client to communicate with Ollama)  
- Additional packages as needed, such as `httpx`, `django`, and `notion-client`.

Make sure Ollama is installed and running locally before using the application.

---

## Environment Variables / API Keys

The application requires the following API keys to function:

- **NOTION_API_KEY**  
  Your Notion integration key for accessing Notion pages and content.

- **CLAUDE_API_KEY**  
  API key for Claude or any other external service used for content processing or generation.

**Important:** Set these keys securely in your environment variables or via a `.env` file.

---

## Disclaimer

This software is provided *as is*, without warranties of any kind.  
The authors assume no liability for any damages or losses arising from the use of this software, including negligence.  
Use it at your own risk.

---

## Getting Started

1. Clone this repository.

2. Install Python dependencies:
     + Django 

4. Install the LLaMA 3 model with Ollama:

   ```
   ollama pull llama3
   ```

5. Set environment variables in PowerShell within your project directory:

   ```
   Change the variables within the views.py and the llm.py files to reflect your Notion API and Claude API Keys 
   ```

6. Start the Ollama server:

   ```
   ollama serve
   ```

7. Run the Django development server:

   ```
   python manage.py runserver
   ```

8. Open your browser and navigate to [http://localhost:8000](http://localhost:8000) to access the app.

