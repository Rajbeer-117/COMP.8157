# Hybrid Cybersecurity Threat Intelligence Retrieval Benchmark

A runnable COMP.8157 project for comparing hybrid semantic + structured retrieval across:

- PostgreSQL 16 + pgvector
- Milvus 2.x
- Weaviate

The project uses cybersecurity records such as CVE/NVD-style vulnerabilities and MITRE ATT&CK-style techniques. It supports structured filters such as severity, platform, publication date, source, and tactic, combined with semantic similarity search over generated embeddings.

## Project objective

The goal is to evaluate how vector database systems behave when cybersecurity analysts ask hybrid queries such as:

> Find vulnerabilities semantically similar to "remote code execution in Windows service" where severity >= 8.0 and platform = Windows.

The benchmark records latency, recall@k, result quality, indexing time, and index/storage size where available.

## Team roles used in this project

| Member | Role | Main responsibility |
|---|---|---|
| Rajbeer Kaur Dutta | Data Engineering & Documentation Lead | Dataset collection, schema design, embeddings, documentation, reports |
| Krishkumar Patel | System Configuration, Deployment & Optimization Lead | PostgreSQL, Milvus, Weaviate, Docker, indexing, performance monitoring |
| Sindhu Padmaja Dudekula | Benchmark, Metrics & Result Analysis Lead | Query templates, benchmark execution, latency/recall metrics, graphs |

## Folder structure

```text
hybrid_cyber_vector_project/
├── backend/                 # FastAPI demo backend
├── data/                    # sample data and generated processed data
├── docs/                    # report-ready project notes
├── frontend/                # simple web UI
├── scripts/                 # setup and helper scripts
├── src/                     # main Python package
│   ├── db/                  # database adapters
│   └── evaluation/          # metrics and benchmark logic
├── docker-compose.yml       # PostgreSQL, Milvus, Weaviate
├── requirements.txt
├── run_sample.py            # local demo without external DBs
└── Makefile
```

## Quick start: local sample demo

This command runs a local exact-search demo using the sample cybersecurity dataset. It does not require Docker.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python run_sample.py
```

Output is saved to:

```text
data/results/local_sample_results.json
```

## Full database benchmark setup

The full benchmark needs Docker Desktop and the full dependency file. If `docker` is not recognized, install/open Docker Desktop and restart VS Code.

```bash
pip install -r requirements-full.txt
```

Start the database services:

```bash
docker compose up -d postgres weaviate etcd minio milvus
```

Initialize PostgreSQL with pgvector tables:

```bash
python -m scripts.init_postgres
```

Prepare the sample dataset and embeddings:

```bash
python -m scripts.prepare_data --input data/sample_cyber_docs.jsonl --output data/processed_docs.jsonl
```

Load data into PostgreSQL:

```bash
python -m scripts.load_postgres --input data/processed_docs.jsonl
```

Load data into Milvus:

```bash
python -m scripts.load_milvus --input data/processed_docs.jsonl
```

Load data into Weaviate:

```bash
python -m scripts.load_weaviate --input data/processed_docs.jsonl
```

Run the benchmark:

```bash
python -m scripts.run_benchmark --systems postgres milvus weaviate --queries data/benchmark_queries.json --output data/results/benchmark_results.json
```

Generate charts:

```bash
python -m scripts.plot_results --input data/results/benchmark_results.json --output docs/results_charts
```

Run the demo backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

Open the frontend:

```text
frontend/index.html
```

## Dataset options

The included sample dataset is intentionally small so the project can be demonstrated easily. For the final experiment, replace it with larger NVD/CVE and MITRE ATT&CK exports.

Recommended scale levels for the final report:

| Dataset tier | Purpose |
|---|---|
| 50K records | prototype and baseline results |
| 250K records | realistic NVD-scale experiment |
| 1M records | scalability stress test |

## Metrics collected

- Query latency in milliseconds
- P50, P95, and P99 latency
- Recall@10 and recall@50 against exact-search baseline
- Index/build/load time
- Result ranking agreement
- Filter selectivity effect

## Report-ready novelty statement

This project does not only test pure vector similarity search. It evaluates the interaction between structured filtering and semantic retrieval in a cybersecurity setting. The important insight is that metadata filters such as severity, platform, date range, and MITRE tactic can change both latency and recall because each database integrates vector indexes and predicate filtering differently.

## Notes for GitHub commits

Suggested commit sequence:

1. `init: add project structure and docker compose`
2. `data: add cybersecurity sample schema and preprocessing pipeline`
3. `db: add postgres pgvector loader and query adapter`
4. `db: add milvus and weaviate adapters`
5. `benchmark: add hybrid query templates and metrics`
6. `docs: add midterm progress notes and team task breakdown`
7. `frontend: add simple search demo interface`
8. `results: add benchmark output and charts`

## Academic integrity note

Use this as a project implementation base and personalize the results, GitHub history, screenshots, and report explanation using your own executed experiments.
