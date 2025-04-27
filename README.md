# AI Search Metrics

A tool for measuring and analyzing brand mentions in AI search engine responses.

## Features

- Query multiple AI search providers (Perplexity, Gemini, OpenAI)
- Analyze brand mentions in responses
- Compare target brand vs competitor mentions
- Sentiment analysis of brand mentions
- Data visualization with charts and graphs
- GUI for easy interaction and data display

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -e .
   ```
3. Create a `.env` file with your API keys:
   ```
   PPLX_API_KEY=your_perplexity_api_key
   PPLX_MODEL_NAME=your_perplexity_model
   GOOGLE_API_KEY=your_google_api_key
   GEMINI_MODEL_NAME=your_gemini_model
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL_NAME=your_openai_model
   SPREADSHEET_ID=your_google_sheet_id (optional)
   ```
4. If using Google Sheets, place your `google_sheets_credentials.json` in the root directory.

## Usage

### GUI Application

Run the GUI application:

```
python gui_app.py
```

The GUI allows you to:
- Set target and competitor brands
- Enter search queries
- Select which AI providers to use
- View raw responses
- View brand mention statistics
- See mention context and sentiment analysis
- Visualize the results with charts

### Command Line

Run the command line version:

```
python main.py
```

## Structure

- `gui_app.py`: GUI application using Tkinter
- `main.py`: Command line application
- `metrics.py`: Metrics calculation functions
- `llm_integrations/`: Integrations with AI providers
  - `perplexity_integration.py`: Perplexity AI integration
  - `gemini_integration.py`: Google Gemini integration
  - `openai_integration.py`: OpenAI integration
  - `sentiment_analysis.py`: Sentiment analysis of responses
- `utils/`: Utility functions
  - `gsheet_interactions.py`: Google Sheets interaction
  - `logger.py`: Logging utilities