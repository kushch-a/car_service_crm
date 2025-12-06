import asyncio
import httpx
import random
import time

TARGET_URL = "http://backend:8000"
ENDPOINTS = [
    "/",
    "/health",
    "/customers",
    "/cars",
    "/services",
    "/invoices",
    "/users",
    "/non-existent-page",
    "/error"
]

async def make_request(client, endpoint):
    try:
        url = f"{TARGET_URL}{endpoint}"
        print(f"Requesting {url}...")
        response = await client.get(url, timeout=10.0)
        print(f"Response from {url}: {response.status_code}")
    except httpx.RequestError as e:
        print(f"Error requesting {e.request.url}: {e}")

async def main():
    print("Starting load generator...")
    async with httpx.AsyncClient() as client:
        while True:
            # Вибираємо випадковий ендпоінт
            endpoint = random.choice(ENDPOINTS)
            
            # Збільшимо ймовірність виклику /error для швидшого спрацювання алерту
            if random.random() < 0.3: # 30% шанс
                endpoint = "/error"

            tasks = [make_request(client, endpoint) for _ in range(random.randint(1, 3))]
            await asyncio.gather(*tasks)
            
            await asyncio.sleep(random.uniform(0.5, 1.5))

if __name__ == "__main__":
    asyncio.run(main())
