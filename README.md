

## Why we have this

PR [774](https://github.com/opea-project/GenAIComps/pull/774),
[957](https://github.com/opea-project/GenAIExamples/pull/957)

## Prerequisites

TODO

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

Baseline/Feature megaservices both listen to 8888.