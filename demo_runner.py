import asyncio
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv() 

from llm_integrations.perplexity_integration import PerplexityIntegration
from llm_integrations.gemini_integration      import GeminiIntegration
from llm_integrations.openai_integration      import OpenAIIntegration
from llm_integrations.sentiment_analysis      import SentimentAnalysis
ProviderResult = Dict  # -> the same dict shape your provider classes return

def add_sentiment_analysis(results: List[ProviderResult]) -> List[ProviderResult]:
    """Add sentiment analysis to results synchronously."""
    try:
        analyzer = SentimentAnalysis()
        contexts = [r.get("brand_mention_context") for r in results if r.get("brand_mention_context")]
        if contexts:
            sentiments = analyzer.predict_sentiment(contexts)
            # Add sentiments back to the original results
            context_index = 0
            for result in results:
                if result.get("brand_mention_context"):
                    result["sentiment"] = sentiments[context_index]
                    context_index += 1
    except Exception as e:
        print(f"Error running sentiment analysis: {e}")
        # Continue without sentiment analysis if it fails
    return results

async def run_all(
    brand: str,
    competitor: str,
    queries: List[str],
    repeat_count: int = 1
) -> List[ProviderResult]:
    """Run all providers concurrently and flatten the results."""
    providers = [
        PerplexityIntegration(brand_name=brand, competitor_name=competitor),
        GeminiIntegration(brand_name=brand, competitor_name=competitor),
        OpenAIIntegration(brand_name=brand, competitor_name=competitor),
    ]
    queries = queries * repeat_count
    tasks = [p.batch_query_perplexity(queries) if p.provider_name == "Perplexity"
             else p.batch_query_gemini(queries) if p.provider_name == "Gemini"
             else p.batch_query_openai(queries)
             for p in providers]

    nested_results: List[List[ProviderResult]] = await asyncio.gather(*tasks)
    # flatten so Streamlit can loop easily
    results = [item for sub in nested_results for item in sub]
    
    return results

async def run_analysis(analysis_prompt: str) -> str:
    """Run the analysis prompt through an LLM provider."""
    try:
        provider = OpenAIIntegration()
        response = await provider.query_openai(analysis_prompt)
        return response.get("response_text", "Analysis failed to generate.")
    except Exception as e:
        print(f"Error running analysis: {e}")
        return "Analysis failed to generate due to an error."
