from anthropic import Anthropic
import json
import os
from dotenv import load_dotenv
import asyncio
from metrics import has_brand_mention

load_dotenv()

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL_NAME = os.getenv("CLAUDE_MODEL_NAME")

# TODO: Look into batching!! This seems very simple in Anthropic integration
class ClaudeIntegration:
    def __init__(self, model_name=CLAUDE_MODEL_NAME, api_key=CLAUDE_API_KEY, brand_name="Avanza", competitor_name="Nordnet"):
        self.client = Anthropic(api_key=api_key)
        self.model_name = model_name
        self.brand_name = brand_name
        self.competitor_name = competitor_name
        self.provider_name = "Claude"

    async def query_claude(self, query_text):
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=500,
            messages=[
                {"role": "user", "content": query_text}
            ],
            tools=[{
                "type":"web_search_20250305",
                "name": "web_search",
                "max_uses": 2
            }],
        )
        
        response_text = await self.extract_response_text(response)
        search_urls = await self.extract_search_urls(response)
        brand_mention, competitor_mention = await self.extract_brand_mentions(response, self.brand_name, self.competitor_name)
        brand_mention_context = await self.extract_brand_mention_context(response, self.brand_name)
        
        output = dict(brand_name=self.brand_name,
                provider_name=self.provider_name,
                model_name=self.model_name,
                query_text=query_text, 
                response=response, 
                response_text=response_text, 
                search_urls=search_urls, 
                brand_mention=brand_mention, 
                competitor_mention=competitor_mention,
                brand_mention_context=brand_mention_context)

        return output
    
    
    async def batch_query_claude(self, queries):
        responses = await asyncio.gather(*[self.query_claude(query) for query in queries])

        return responses
    
    async def extract_response_text(self, response):
        text = ""
        for content in response.content:
            if content.type == "text":
                text += content.text
        return text
    
    async def extract_search_urls(self, response):
        urls = []
        for content in response.content:
            if content.type == "text":
                if content.citations is not None:
                    for citation in content.citations:
                        urls.append(citation.url)
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
            
    async def extract_brand_mentions(self, response, brand_name, competitor_name):
        text = await self.extract_response_text(response)
        brand_mention = await has_brand_mention(text, brand_name)
        competitor_mention = await has_brand_mention(text, competitor_name)
        return brand_mention, competitor_mention
    
async def main():
    claude_integration = ClaudeIntegration()
    response = await claude_integration.query_claude("What's the best service to trade stocks in Sweden?")
    for content in response.content:
        if content.type == "text":
            print(content.text)
            if content.citations is not None:
                for citation in content.citations:
                    print(citation.url)
                    print(citation.title)

if __name__ == "__main__":
    asyncio.run(main())