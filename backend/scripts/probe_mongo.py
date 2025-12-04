import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys

async def probe_mongo():
    uris = [
        "mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin",
        "mongodb://127.0.0.1:27017/national_indicator"
    ]

    for uri in uris:
        print(f"Trying URI: {uri.split('@')[-1] if '@' in uri else uri} ...") # Hide password in logs
        try:
            client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=2000)
            # Force a command to check connection
            await client.admin.command('ping')
            print(f"SUCCESS! Connected with: {uri}")
            return
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(probe_mongo())
