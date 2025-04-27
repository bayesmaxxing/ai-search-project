import asyncio
import google.generativeai as genai
from google.generativeai.types import Tool, GenerateContentConfig, GoogleSearchRetrieval
import os 
from dotenv import load_dotenv
from metrics import has_brand_mention

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

class GeminiIntegration:
    def __init__(self, model_name=GEMINI_MODEL_NAME, api_key=GEMINI_API_KEY, brand_name="Avanza", competitor_name="Nordnet"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.brand_name = brand_name
        self.competitor_name = competitor_name
        self.provider_name = "Gemini"

    async def query_gemini(self, query_text):
        google_search_tool = Tool(
            google_search_retrieval = GoogleSearchRetrieval()
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=query_text,
            config=GenerateContentConfig(
                    tools=[google_search_tool],
                    response_modalities=["TEXT"],
                )
            )
        
        response_text = await self.extract_response_text(response)
        search_urls = await self.extract_search_urls(response)
        brand_mention = await self.extract_brand_mentions(response, self.brand_name)
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
    
    async def batch_query_gemini(self, queries):
        responses = await asyncio.gather(*[self.query_gemini(query) for query in queries])

        return responses
    
    async def extract_response_text(self, response):
        return response.candidates[0].content.parts[0].text.replace('*', '')
    
    
    async def extract_search_urls(self, response):
        grounding_supports = response.candidates[0].grounding_metadata.grounding_chunks
        grounding_urls = [(chunk.web.uri, chunk.web.title) for chunk in grounding_supports if chunk.web]
        return grounding_urls
    
    async def extract_brand_mention_context(self, response, brand_name):
        response_text = response.candidates[0].content.parts[0].text.replace('*', '')
        if brand_name.lower() not in response_text.lower():
            return None
        
        brand_index = response_text.lower().find(brand_name.lower())
        text_after_brand = response_text[brand_index:]

        import re
        sentences = re.split(r'(?<=[.!?])\s+', text_after_brand)
        
        result_sentences = sentences[:min(3, len(sentences))]
        result = ' '.join(result_sentences)
        
        return result
    
    # CALCULATING METRICS AND SUMMARIZING
    async def extract_brand_mentions(self, response, brand_name):
        response_text = await self.extract_response_text(response)
        mention = await has_brand_mention(response_text, brand_name)
        return mention
    
    
        

async def main():
    gemini_integration = GeminiIntegration(model_name=GEMINI_MODEL_NAME, api_key=GEMINI_API_KEY)
    queries = [
        "Can you give me some information about the best trading apps in sweden?",
    ]
    
    response = await gemini_integration.query_gemini(queries[0])
    
    print(response["response_text"])
    print(response["search_urls"])
    print(response["brand_mention"])
    print(response["brand_mention_context"])

if __name__ == "__main__":
    asyncio.run(main())