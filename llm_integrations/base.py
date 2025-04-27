from abc import ABC, abstractmethod
from typing import List, Dict

class BaseProvider(ABC):
    provider_name: str

    def __init__(self, brand_name: str, competitor_name: str):
        self.brand_name = brand_name
        self.competitor_name = competitor_name

    @abstractmethod
    async def batch_query(self, queries: List[str]) -> List[Dict]:
        ...
