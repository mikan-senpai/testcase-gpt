import os
import io
from typing import List, Optional
from pathlib import Path
import json

import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI, AzureOpenAI
from fastapi.responses import Response

# Load env from common locations
load_dotenv(find_dotenv(usecwd=True), override=False)
src_dir = Path(__file__).resolve().parent
load_dotenv(src_dir / ".env", override=False)
load_dotenv(src_dir.parent / ".env", override=False)

# In-memory context parsed from latest uploads
DATA_CONTEXT: List[dict] = []

# Initialize client (prefer Azure)
AZURE_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
HF_TOKEN = os.environ.get("HF_TOKEN")

client = None
MODEL_NAME: Optional[str] = None

if AZURE_ENDPOINT and AZURE_API_KEY and AZURE_DEPLOYMENT:
    client = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
    )
    MODEL_NAME = AZURE_DEPLOYMENT
else:
    if HF_TOKEN:
        client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=HF_TOKEN)
        MODEL_NAME = "moonshotai/Kimi-K2-Instruct"

app = FastAPI(title="Simple LlamaIndex Analyzer API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Quiet favicon 404s
@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return Response(status_code=204)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    sqlQuery: str
    description: str


def parse_excel_to_context_from_uploads(files: List[UploadFile]) -> List[dict]:
    """Mirror of parse_excel_to_context but for uploaded files (file-like)."""
    all_content: List[dict] = []

    for uf in files:
        try:
            content = io.BytesIO(uf.file.read())
            excel_file = pd.ExcelFile(content)
            file_name = uf.filename

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(content, sheet_name=sheet_name)
                context = {
                    "file": file_name,
                    "sheet": sheet_name,
                    "columns": df.columns.tolist(),
                    "num_rows": int(len(df)),
                    "sample_data": df.head(5).to_dict(),
                    "data_types": df.dtypes.astype(str).to_dict(),
                    "null_counts": df.isnull().sum().to_dict(),
                    "unique_counts": {col: int(df[col].nunique()) for col in df.columns},
                }
                numeric_cols = df.select_dtypes(include=["number"]).columns
                if len(numeric_cols) > 0:
                    context["statistics"] = df[numeric_cols].describe().to_dict()
                all_content.append(context)
        except Exception as e:
            all_content.append({"file": uf.filename, "error": str(e)})

    return all_content

@app.get("/api/health")
async def health():
    provider = "azure" if (AZURE_ENDPOINT and AZURE_API_KEY and AZURE_DEPLOYMENT) else ("huggingface" if HF_TOKEN else "none")
    return {"ok": True, "provider": provider, "model": MODEL_NAME, "context_items": len(DATA_CONTEXT)}

@app.post("/api/context/upload")
async def context_upload(files: List[UploadFile] = File(...)):
    global DATA_CONTEXT
    before = len(DATA_CONTEXT)
    new_items = parse_excel_to_context_from_uploads(files)
    # Append only new parsed entries
    DATA_CONTEXT.extend(new_items)
    return {"ok": True, "added": len(new_items), "total": len(DATA_CONTEXT)}

_HEURISTICS = [
    (
        ["select", "all", "data", "records"],
        (
            "SELECT * FROM user_data ORDER BY created_date DESC;",
            "Retrieve all records ordered by creation date.",
        ),
    ),
    (
        ["count", "total", "number"],
        ("SELECT COUNT(*) AS total_records FROM user_data WHERE status = 'active';", "Count active records."),
    ),
    (
        ["average", "avg", "mean"],
        ("SELECT AVG(amount) AS average_amount FROM user_data WHERE amount > 0;", "Average of non-zero amounts."),
    ),
    (
        ["group", "category", "breakdown"],
        (
            "SELECT category, COUNT(*) AS count, SUM(amount) AS total FROM user_data GROUP BY category ORDER BY total DESC;",
            "Group by category with counts and totals.",
        ),
    ),
    (
        ["duplicate"],
        ("SELECT email, COUNT(*) AS duplicates FROM user_data GROUP BY email HAVING COUNT(*) > 1;", "Find duplicate emails."),
    ),
]

@app.post("/api/chat-sql", response_model=ChatResponse)
async def chat_sql(req: ChatRequest):
    user_message = req.message.strip()

    if client and MODEL_NAME and DATA_CONTEXT:
        try:
            context_str = json.dumps(DATA_CONTEXT, indent=2, default=str)
            prompt = f"""
You are a Senior QA Engineer. Use the following Data Context (summaries of uploaded Excel sheets) to answer.
Return a JSON object with fields "sqlQuery" and "description".

Data Context:
{context_str}

User request: {user_message}
Format strictly as JSON.
"""
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "Return only JSON with sqlQuery and description."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=600,
                temperature=0.3,
            )
            content = completion.choices[0].message.content or ""
            data = json.loads(content)
            sql = data.get("sqlQuery") or data.get("sql") or ""
            desc = data.get("description") or "Suggested SQL."
            if sql:
                return ChatResponse(sqlQuery=sql, description=desc)
        except Exception:
            pass

    # Heuristic fallback
    lower = user_message.lower()
    for triggers, (sql, desc) in _HEURISTICS:
        if any(t in lower for t in triggers):
            return ChatResponse(sqlQuery=sql, description=desc)
    return ChatResponse(
        sqlQuery='SELECT column_name, data_type FROM information_schema.columns WHERE table_name = "user_data";',
        description='Show the structure of the user_data table.',
    )

# Run local dev: uvicorn backend.server:app --reload --port 8000
