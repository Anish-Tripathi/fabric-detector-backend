# Fabric Defect Detection — FastAPI Backend

A clean, production-ready FastAPI backend that serves a TensorFlow/Keras fabric-defect classification model.

---

## Folder Structure

```
fabric-defect-backend/
├── main.py                  # FastAPI app entry point
├── requirements.txt
├── .env.example             # Copy → .env and fill values
├── .gitignore
├── model.keras              # ← place your trained model here
└── app/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   ├── config.py        # Pydantic-settings (reads .env)
    │   ├── model.py         # ModelManager singleton
    │   └── security.py      # API-key dependency
    ├── routes/
    │   ├── __init__.py
    │   └── predict.py       # POST /api/v1/predict
    └── schemas/
        ├── __init__.py
        └── predict.py       # Request / response Pydantic models
```

---

## Quick Start

### 1. Clone & create virtual environment

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
# Edit .env — set API_KEY, MODEL_PATH, ALLOWED_ORIGINS
```

### 4. Place your model

Copy your trained model file into the project root:

```bash
cp /path/to/your/model.keras ./model.keras
```

### 5. Run the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs → http://localhost:8000/docs

---

## API Reference

### `POST /api/v1/predict`

**Headers**
| Key | Value |
|-----|-------|
| `x-api-key` | your API key |

**Body** — `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| `file` | File | Fabric image (JPEG / PNG / WebP / BMP) |

**Response 200**

```json
{
  "prediction": "Defective",
  "confidence": 0.87
}
```

**Response 401**

```json
{ "detail": "Invalid or missing API key." }
```

---

## Frontend Integration (JavaScript example)

```javascript
const formData = new FormData();
formData.append("file", imageFile); // File object from <input type="file">

const response = await fetch("http://localhost:8000/api/v1/predict", {
  method: "POST",
  headers: { "x-api-key": "mysecret123" },
  body: formData,
});

const data = await response.json();
console.log(data.prediction); // "Good" | "Defective"
console.log(data.confidence); // e.g. 0.87
```

---

## Deployment (Render / Railway / Fly.io)

Set the following environment variables in your hosting dashboard:

- `API_KEY` — strong secret
- `MODEL_PATH` — path to model file after deploy
- `ALLOWED_ORIGINS` — your frontend URL

Start command:

```
uvicorn main:app --host 0.0.0.0 --port $PORT
```
