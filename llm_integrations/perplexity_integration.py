import requests
import asyncio
from dotenv import load_dotenv
import os
from metrics import has_brand_mention

load_dotenv()

PPLX_API_KEY = os.getenv("PPLX_API_KEY")
PPLX_MODEL_NAME = os.getenv("PPLX_MODEL_NAME")

class PerplexityIntegration:
    def __init__(self, model_name=PPLX_MODEL_NAME, api_key=PPLX_API_KEY, brand_name="Avanza", competitor_name="Nordnet"):
        self.model_name = model_name
        self.api_key = api_key
        self.brand_name = brand_name
        self.competitor_name = competitor_name
        self.provider_name = "Perplexity"

    async def query_perplexity(self, query_text):
        """Sends a query to the configured Perplexity model and returns the response text."""    
        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that can answer questions and help with tasks."},
                {"role": "user", "content": query_text}
            ],
            "max_tokens": 2000
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        with requests.post(url, json=payload, headers=headers) as response:
            response.raise_for_status()
            data = response.json()
        
        response_text = await self.extract_response_text(data)
        search_urls = await self.extract_search_urls(data)
        brand_mention = await self.extract_brand_mentions(data, self.brand_name)
        brand_mention_context = await self.extract_brand_mention_context(data, self.brand_name)
        
        output =  dict(brand_name=self.brand_name, 
                       provider_name=self.provider_name, 
                       model_name=self.model_name, 
                       query_text=query_text, 
                       response=response, 
                       response_text=response_text, 
                       search_urls=search_urls, 
                       brand_mention=brand_mention, 
                       brand_mention_context=brand_mention_context)

        return output
        
    async def batch_query_perplexity(self, queries):
        """Process multiple Perplexity queries concurrently with rate limiting."""
        responses = await asyncio.gather(*[self.query_perplexity(query) for query in queries])

        return responses
    
    async def extract_response_text(self, response):
        return response["choices"][0]["message"]["content"]
    
    async def extract_search_urls(self, response):
        return response["citations"]
    
    async def extract_brand_mention_context(self, response, brand_name):
        response_text = await self.extract_response_text(response)
        if brand_name.lower() not in response_text.lower():
            return None
        
        brand_index = response_text.lower().find(brand_name.lower())
        text_after_brand = response_text[brand_index:]

        import re
        sentences = re.split(r'(?<=[.!?])\s+', text_after_brand)
        
        result_sentences = sentences[:min(3, len(sentences))]
        result = ' '.join(result_sentences)

        return result
    
    async def extract_brand_mentions(self, response, brand_name):
        response_text = await self.extract_response_text(response)
        mention = await has_brand_mention(response_text, brand_name)
        return mention
    
async def main():
    perplexity_integration = PerplexityIntegration()
    response = await perplexity_integration.query_perplexity("What's the best service to trade stocks in Sweden?")
    
    print(response["response_text"])
    print(response["search_urls"])
    print(response["brand_mention"])
    print(response["brand_mention_context"])

if __name__ == "__main__":
    asyncio.run(main())