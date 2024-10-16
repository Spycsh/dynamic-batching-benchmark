import asyncio
import aiohttp
import time
import random
import numpy as np
import argparse




latencies = []

async def send_request(session, request_id):
    try:
        if args.setting == 1:
            url = urls[0]
            payload = payloads[0]
        elif args.setting == 2:
            url = urls[1]
            payload = payloads[1]
        else:
            idx = random.randint(0,1)
            url = urls[idx]
            payload = payloads[idx]

        start_time = time.time()
        async with session.post(url, json=payload, headers={'Content-Type': 'application/json'}) as response:
            # Process response if needed
            result = await response.json()
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
    total_requests = 128
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
    parser.add_argument("--setting", type=int, default=1, help="Setting 1: all embedding; Setting 2: all reranking; Setting 3: random embedding random reranking")
    parser.add_argument("--baseline", action="store_true", help="bench baseline")
    args = parser.parse_args()

    if args.baseline:
        urls = ["http://localhost:8090/v1/embeddings", "http://localhost:8808/rerank"]
        payloads = [
            {"input": "What is Deep Learning?"}, 
            {"query": "What is Deep Learning?",
            "texts": ["Deep Learning is not...", "Deep learning is..."],}
        ]
    else:
        urls = ["http://localhost:6001/v1/embeddings", "http://localhost:6001/v1/reranking"]
        payloads = [
            {"text": "What is Deep Learning?"}, 
            {"initial_query": "What is Deep Learning?",
            "retrieved_docs": [{"text":"Deep Learning is not..."}, {"text":"Deep learning is..."}],
            "top_n": 2}
        ]

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
