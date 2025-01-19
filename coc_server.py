import json
import os
import re
import urllib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Configuration
CACHE_DIR = "cache"
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.clashofclans.com/v1"
UPDATE_INTERVAL = 12  # hours

app = FastAPI(title="Clash of Clans API Cache")

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CacheManager:
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def _normalize_endpoint(self, endpoint: str) -> str:
        """Normalize endpoint to consistent format for cache keys"""
        # replace non-alphanumeric characters with underscores
        return re.sub(r'[^a-zA-Z0-9]', '_', endpoint)
    
    def get_cache_path(self, endpoint: str) -> Path:
        # Normalize endpoint and clan tag
        normalized_endpoint = self._normalize_endpoint(endpoint)
        return self.cache_dir / f"{normalized_endpoint}.json"
    
    def read_cache(self, endpoint: str) -> Optional[Dict]:
        cache_path = self.get_cache_path(endpoint)
        if not cache_path.exists():
            return None
            
        with cache_path.open('r') as f:
            data = json.load(f)
            if datetime.fromisoformat(data['cached_at']) + timedelta(hours=UPDATE_INTERVAL) < datetime.now():
                return None
            return data['content']
            
    def write_cache(self, endpoint: str, content: Dict):
        cache_path = self.get_cache_path(endpoint)
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'content': content
        }
        with cache_path.open('w') as f:
            json.dump(cache_data, f)

# Update the background task function to use consistent cache keys
async def update_cache(endpoint: str):
    """Background task to update cache"""
    try:
        data = await clash_api.fetch_data(f"{endpoint}")
        # Use the same endpoint normalization as CacheManager
        cache_manager.write_cache(endpoint, data)
    except Exception as e:
        print(f"Error updating cache for {endpoint}: {str(e)}")

class ClashAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
    async def fetch_data(self, endpoint: str) -> Dict:
        async with httpx.AsyncClient() as client:
            # encode endpoint to be safe
            endpoint = urllib.parse.quote(endpoint)
            response = await client.get(
                f"{BASE_URL}{endpoint}",
                headers=self.headers
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Clash API error: {response.text}"
                )
            return response.json()

cache_manager = CacheManager(CACHE_DIR)
clash_api = ClashAPI(API_KEY)


@app.get("/clan/{clan_tag}")
async def get_clan_info(clan_tag: str, background_tasks: BackgroundTasks):
    # Format clan tag
    if not clan_tag.startswith('#'):
        clan_tag = f"#{clan_tag}"
    endpoint = f"/clans/{clan_tag}"
    # Try to get from cache
    cached_data = cache_manager.read_cache(endpoint)
    if cached_data:
        # Schedule background update if needed
        background_tasks.add_task(update_cache, endpoint)
        return cached_data
        
    # If no cache, fetch directly
    data = await clash_api.fetch_data(endpoint)
    cache_manager.write_cache(endpoint, data)
    return data

@app.get("/clan/{clan_tag}/currentwar")
async def get_clan_currentwar(clan_tag: str, background_tasks: BackgroundTasks):
    if not clan_tag.startswith('#'):
        clan_tag = f"#{clan_tag}"
    endpoint = f"/clans/{clan_tag}/currentwar"
        
    cached_data = cache_manager.read_cache(endpoint)
    if cached_data:
        background_tasks.add_task(update_cache, endpoint)
        return cached_data
        
    data = await clash_api.fetch_data(endpoint)
    cache_manager.write_cache(endpoint, data)
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)