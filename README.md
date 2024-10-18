

## Why we have this

PR [774](https://github.com/opea-project/GenAIComps/pull/774),
[957](https://github.com/opea-project/GenAIExamples/pull/957)

Dynamic batching in OPEA is a feature that addresses the problem that we cannot run multiple models concurrently on one Gaudi card. For basic serving, we can start multiple TEI servers on multiple cards. Each server serves one model. For example, the original ChatQnA pipeline uses one TEI server for embedding (requiring one Gaudi card) and another TEI server for reranking (also requiring one Gaudi card), consuming two Gaudi cards. However, the memory requirements on each card are far below the maximum capacity of 94GB per Gaudi card. Therefore, an idea is to run smaller models, such as the embedding and reranking models, on a single Gaudi card and expose a single serving endpoint as a microservice. At the same time, care must be taken to ensure that the model requests are properly buffered/batched to make full use of the original TEI dynamic batching feature. Additionally, each batch inference should remain exclusive due to the Gaudi card's limitations.


## Prerequisites

### Environment

```bash
export host_ip=${your_host_ip}
export HUGGINGFACEHUB_API_TOKEN=xxxx
export no_proxy=${no_proxy}
export http_proxy=${http_proxy}
export https_proxy=${https_proxy}


# embedding-reranking service
export EMBEDDING_MODEL_ID="BAAI/bge-base-en-v1.5"
export RERANK_MODEL_ID="BAAI/bge-reranker-base"

# dataprep
# make sure using local tei model
#export TEI_EMBEDDING_ENDPOINT="http://${host_ip}:6001"  # 8091
export EMBED_MODEL=BAAI/bge-base-en-v1.5
export REDIS_URL="redis://${host_ip}:6379"
export INDEX_NAME="rag-redis"

# tgi
export LLM_MODEL_ID="Intel/neural-chat-7b-v3-3"

# mega
export RETRIEVER_SERVICE_HOST_IP=${host_ip}
export EMBEDDING_RERANK_SERVICE_HOST_IP=${host_ip}
export EMBEDDING_RERANK_SERVICE_PORT=6001
export LLM_SERVER_HOST_IP=${host_ip}
export LLM_SERVER_PORT=8005
export MEGA_SERVICE_HOST_IP=${host_ip}

# ui
export BACKEND_SERVICE_ENDPOINT="http://${host_ip}:8888/v1/chatqna"
export DATAPREP_SERVICE_ENDPOINT="http://${host_ip}:6007/v1/dataprep"
export DATAPREP_GET_FILE_ENDPOINT="http://${host_ip}:6007/v1/dataprep/get_file"
export DATAPREP_DELETE_FILE_ENDPOINT="http://${host_ip}:6007/v1/dataprep/delete_file"
export LOGFLAG=True

# baseline: not conflict with batching
export EMBEDDING_SERVER_HOST_IP=${host_ip}
export RERANK_SERVER_HOST_IP=${host_ip}
export TEI_EMBEDDING_ENDPOINT="http://${host_ip}:8090"
```


Download RAG document and prepare data
```bash
# download pdf file
wget https://raw.githubusercontent.com/opea-project/GenAIComps/main/comps/retrievers/redis/data/nke-10k-2023.pdf
# clear data
curl -X POST "http://${host_ip}:6007/v1/dataprep/delete_file"      -d '{"file_path": "all"}'      -H "Content-Type: application/json"
# upload pdf file with dataprep
curl -X POST "http://${host_ip}:6007/v1/dataprep" \
    -H "Content-Type: multipart/form-data" \
    -F "files=@./nke-10k-2023.pdf"
# make sure file exist
curl -X POST "http://${host_ip}:6007/v1/dataprep/get_file"      -H "Content-Type: application/json"
```


Make sure you have warmup few rounds to stablize the bench output.

### Start server

Go to my branch

* Baseline

Edit the [compose.yaml](./compose.yaml)

```bash
docker compose -f compose.yaml up -d
```

* Dynamic batching

Edit the [compose_dynamic_batching.yaml](./compose_dynamic_batching.yaml)


```bash
docker compose -f compose_dynamic_batching.yaml up -d
```

## microservice benchmarks

```bash
# requests to only embedding
python3 chatqna_micro_bench.py --setting 1
# requests to only reranking
python3 chatqna_micro_bench.py --setting 2
# random request to embedding or reranking
python3 chatqna_micro_bench.py --setting 3
```

To check the baseline, add `--baseline` to the above commands for each setting. e.g. `python3 chatqna_micro_bench.py --setting 2 --baseline`

## megaservice benchmarks

```bash
python3 chatqna_mega_bench.py --url http://localhost:8888/v1/chatqna
```

Baseline/Feature megaservices both listen to 8888. Change localhost to your host ip if needed.

## Results

With fully warmup (normally 2~3 round), the results of 256 requests are as follows:

> Baseline
```
All requests completed in 80.60 seconds
P50 latency: 5.08 seconds
P99 latency: 9.18 seconds
avg latency: 4.97 seconds
```

> Dynamic Batching
```
All requests completed in 83.42 seconds
P50 latency: 5.20 seconds
P99 latency: 9.71 seconds
avg latency: 5.22 seconds
```

Therefore, we use only one Gaudi card to serve two models with dynamic batching. Compared to the baseline that use two Gaudi cards, the performance drop is acceptable.