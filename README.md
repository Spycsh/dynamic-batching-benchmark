

## Why we have this

PR [774](https://github.com/opea-project/GenAIComps/pull/774),
[957](https://github.com/opea-project/GenAIExamples/pull/957)

## Prerequisites


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

## microservice benchmarks

```bash
# requests to only embedding
python3 chatqna_micro_bench.py --setting 1
# requests to only reranking
python3 chatqna_micro_bench.py --setting 1
# random request to embedding or reranking
python3 chatqna_micro_bench.py --setting 3
```

To check the baseline, add `--baseline` to the above commands for each setting

## megaservice benchmarks

```bash
python3 chatqna_mega_bench.py --url http://localhost:8888/v1/chatqna
```

Baseline/Feature megaservices both listen to 8888. Change localhost to your host ip if needed.