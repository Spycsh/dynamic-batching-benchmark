import asyncio
import aiohttp
import time
import random
import numpy as np
import argparse




latencies = []

async def send_request(session, request_id):
    try:
        start_time = time.time()
        async with session.post(url, json=payload, headers={'Content-Type': 'application/json'}) as response:
            # Process response if needed
            # result = await response.json()
            result = ""
            async for chunk in response.content.iter_any():
                result += chunk.decode('utf-8')
            latency = time.time() - start_time
            latencies.append(latency)
            print(f"Request {request_id} completed with status: {response.status}")
            return result
    except Exception as e:
        print(f"Request {request_id} failed: {e}")

async def send_requests_batch(session, batch_size, start_id):
    tasks = []
    for i in range(batch_size):
        request_id = start_id + i
        tasks.append(send_request(session, request_id))
    await asyncio.gather(*tasks)

async def main():
    total_requests = 256
    requests_per_second = 32
    total_batches = total_requests // requests_per_second

    async with aiohttp.ClientSession() as session:
        for batch in range(total_batches):
            print(f"Sending batch {batch + 1}")
            await send_requests_batch(session, requests_per_second, batch * requests_per_second)
            if batch < total_batches - 1:
                await asyncio.sleep(1)  # Sleep for 1 second between batches

# Run the main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, default="http://localhost:8888/v1/chatqna", help="url to megaservice")
    parser.add_argument("--prompt", type=str, default="What is the revenue of Nike in 2023?")
    args = parser.parse_args()

    url = args.url
    payload = {"messages": args.prompt}

    overall_start_time = time.time()
    asyncio.run(main())
    print(f"All requests completed in {time.time() - overall_start_time:.2f} seconds")

    # Calculate P50 and P99 latencies using numpy
    if latencies:
        p50_latency = np.percentile(latencies, 50)
        p99_latency = np.percentile(latencies, 99)
        avg_latency = np.average(latencies)

        print(f"P50 latency: {p50_latency:.2f} seconds")
        print(f"P99 latency: {p99_latency:.2f} seconds")
        print(f"avg latency: {avg_latency:.2f} seconds")
