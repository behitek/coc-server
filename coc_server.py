import os
import traceback
import urllib
from typing import Dict, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Configuration
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.clashofclans.com/v1"
ALLOWED_CLAN = ["2G9YRCRV2", "2QQ0VGYCV", "clanwarleagues"]
app = FastAPI(title="Clash of Clans API Cache")

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ClashAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}'
        }

    def allowed(self, endpoint: str) -> bool:
        # Only allowed to retrieve our clan info
        # If someone tries to retrieve someone else's clan info, they will be blocked
        for clan in ALLOWED_CLAN:
            if clan in endpoint:
                return True
        return False
        
    async def request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        async with httpx.AsyncClient() as client:
            # encode endpoint to be safe
            endpoint = urllib.parse.quote(endpoint)
            if not self.allowed(endpoint):
                raise HTTPException(status_code=403, detail="Endpoint not allowed")
            url = f"{BASE_URL}{endpoint}"
            if method.upper() == 'GET':
                response = await client.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = await client.post(url, headers=self.headers, json=data)
            else:
                raise HTTPException(status_code=405, detail=f"Method {method} not allowed")
                
            if response.status_code != 200:
                print("Response:", response.text)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Clash API error: {response.text}"
                )
            return response.json()

clash_api = ClashAPI(API_KEY)

@app.get("/{path:path}")
async def forward_get(path: str):
    try:
        return await clash_api.request('GET', f"/{path}")
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="Invalid request")

@app.post("/{path:path}")
async def forward_post(path: str, data: Dict):
    try:
        return await clash_api.request('POST', f"/{path}", data)
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="Invalid request")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)