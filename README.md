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

## MongoDB

From the `docker` directory, copy the example env file and set the root username and password:

```bash
cd docker
cp .env.example .env
docker compose up -d
```

Those credentials are created only the first time the data volume is empty. MongoDB listens on `127.0.0.1:27007`.

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

`.env.example` does not include the MongoDB keys. Add them after copying it. The root user lives in the `admin` database, so the URI needs `authSource=admin`. Use the same username and password as `docker/.env`:

```bash
MONGO_URI=mongodb://<username>:<password>@127.0.0.1:27007/mini-rag?authSource=admin
MONGO_DB_NAME=mini-rag
```

## Run the API

From the `src` directory:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs are at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Endpoints

- `GET /api/v1/` — returns the app name and version from settings.
- `POST /api/v1/data/upload/{project_id}` — accepts a multipart file in the `file` field. Plain text and PDF files within `FILE_MAX_SIZE` are stored under `src/assets/files/{project_id}/`. The project is created in the `projects` collection when it does not already exist. A successful response includes `file id` (the stored name, including its random prefix) and `project_id` (the project's MongoDB id).
- `POST /api/v1/data/process/{project_id}` — JSON body:

```json
{
  "file_id": "stored-file-name.txt",
  "chunk_size": 100,
  "overlap_size": 20,
  "do_reset": false
}
```

`file_id` must match the `file id` returned by upload. `chunk_size` defaults to 100 and `overlap_size` defaults to 20. The file is loaded, split into chunks, and inserted into the `chunks` collection. When `do_reset` is `true`, existing chunks for that project are deleted before the new chunks are inserted. A successful response includes `message` and `inserted_count`. A missing or unknown `file_id` returns `404`.
