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

From the `src` directory:

```bash
pip install -r requirements.txt
```

## Environment

Copy `.env.example` to `.env` inside `src`:

```bash
cp .env.example .env
```

`.env` expects:

- `APP_NAME`
- `APP_VERSION`
- `OPENAI_API_KEY`
- `FILE_TYPES` — JSON list of allowed MIME types, for example `["text/plain","application/pdf"]`
- `FILE_MAX_SIZE` — maximum upload size in megabytes
- `FILE_CHUNK_SIZE` — number of bytes read from the upload at a time

## Run the API

From the `src` directory:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs are at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Endpoints

- `GET /api/v1/` — returns the app name and version from settings.
- `POST /api/v1/data/upload/{project_id}` — accepts a multipart file in the `file` field. Plain text and PDF files within `FILE_MAX_SIZE` are stored under `src/assets/files/{project_id}/`. A successful response includes the stored file id.
