# mini-rag

## Requirements

Python 3.8 or later

## Install Python with Miniconda

1. Download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
2. Create and activate a new environment:

```bash
conda create -n mini-rag python=3.8
conda activate mini-rag
```

## Install required packages

```bash
pip install -r requirements.txt
```

## Environment

Copy `.env.example` to `.env` and set your OpenAI API key:

```bash
cp .env.example .env
```

`.env` expects:

- `APP_NAME`
- `APP_VERSION`
- `OPENAI_API_KEY`
