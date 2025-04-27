from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import asyncio
from metrics import has_brand_mention
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")


class OpenAIIntegration:
    def __init__(self, model_name=OPENAI_MODEL_NAME, api_key=OPENAI_API_KEY, brand_name="Avanza", competitor_name="Nordnet"):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.brand_name = brand_name
        self.competitor_name = competitor_name
        self.provider_name = "OpenAI"

    async def query_openai(self, query_text):
        response = self.client.responses.create(
            model=self.model_name,
            tools=[{"type":"web_search_preview"}],
            tool_choice={"type": "web_search_preview"},
            input=query_text
        )
        
        response_text = await self.extract_response_text(response)
        search_urls = await self.extract_search_urls(response)
        brand_mention = await self.count_brand_mentions(response, self.brand_name)
        brand_mention_context = await self.extract_brand_mention_context(response, self.brand_name)
        
        output = dict(brand_name=self.brand_name,
                provider_name=self.provider_name,
                model_name=self.model_name,
                query_text=query_text, 
                response=response, 
                response_text=response_text, 
                search_urls=search_urls, 
                brand_mention=brand_mention, 
                brand_mention_context=brand_mention_context)

        return output
    
    async def batch_query_openai(self, queries):
        responses = await asyncio.gather(*[self.query_openai(query) for query in queries])

        return responses
    
    async def extract_response_text(self, response):
        return response.output_text
    
    async def extract_search_urls(self, response):
        urls = []
        if response.output[1].content[0].annotations is not None:
            for annotation in response.output[1].content[0].annotations:
                urls.append(annotation.url)
        return urls

    async def extract_brand_mention_context(self, response, brand_name):
        text = await self.extract_response_text(response)
        if brand_name.lower() not in text.lower():
            return None
        
        brand_index = text.lower().find(brand_name.lower())
        text_after_brand = text[brand_index:]

        import re
        sentences = re.split(r'(?<=[.!?])\s+', text_after_brand)
        
        result_sentences = sentences[:min(3, len(sentences))]
        result = ' '.join(result_sentences)
        
        return result
            
    async def count_brand_mentions(self, response, brand_name):
        text = await self.extract_response_text(response)
        mention = await has_brand_mention(text, brand_name)
        return mention
    
async def main():
    openai_integration = OpenAIIntegration()
    response = await openai_integration.query_openai("What's the best service to trade stocks in Sweden?")
    print(response["response_text"])
    print(response["search_urls"])
    print(response["brand_mention"])
    print(response["brand_mention_context"])

if __name__ == "__main__":
    asyncio.run(main())