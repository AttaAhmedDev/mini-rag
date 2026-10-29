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
- `MONGO_URI` — MongoDB connection string
- `MONGO_DB_NAME` — database name, for example `mini-rag`

`.env.example` does not include the MongoDB keys. Add them after copying it. When the API runs on the host and MongoDB is published by Docker Compose, use:

```bash
MONGO_URI=mongodb://127.0.0.1:27007/mini-rag
MONGO_DB_NAME=mini-rag
```

## MongoDB

From the repository root:

```bash
docker compose -f docker/docker-compose.yml up -d
```

MongoDB listens on `127.0.0.1:27007`.

## Run the API

From the `src` directory:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs are at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Endpoints

- `GET /api/v1/` — returns the app name and version from settings.
- `POST /api/v1/data/upload/{project_id}` — accepts a multipart file in the `file` field. Plain text and PDF files within `FILE_MAX_SIZE` are stored under `src/assets/files/{project_id}/`. The project is created in MongoDB when it does not already exist. A successful response includes the stored file id and the project's MongoDB id.
- `POST /api/v1/data/process/{project_id}` — JSON body with `file_id`, and optional `chunk_size` (default 100) and `overlap_size` (default 20). Loads the uploaded file, splits it into chunks, and inserts those chunks into MongoDB. A successful response includes `success` and `inserted_count`.
