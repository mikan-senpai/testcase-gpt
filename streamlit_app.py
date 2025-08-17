import os
import io
import json
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI, AzureOpenAI

# Load environment variables from .env (search upwards and fallback to repo paths)
load_dotenv(find_dotenv(usecwd=True), override=False)
script_dir = Path(__file__).resolve().parent
load_dotenv(script_dir / ".env", override=False)
load_dotenv(script_dir.parent / ".env", override=False)

# Prefer Azure OpenAI if configured, otherwise use HuggingFace router
AZURE_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

client = None
MODEL_NAME = None
PROVIDER = None

if AZURE_ENDPOINT and AZURE_API_KEY and AZURE_DEPLOYMENT:
    client = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
    )
    MODEL_NAME = AZURE_DEPLOYMENT
    PROVIDER = "Azure OpenAI"
else:
    HF_TOKEN = os.environ.get("HF_TOKEN")
    if HF_TOKEN:
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=HF_TOKEN,
        )
        MODEL_NAME = "moonshotai/Kimi-K2-Instruct"
        PROVIDER = "Hugging Face Inference API"

# --------------------------- Core logic (reused) ---------------------------

def parse_excel_to_context_from_uploads(files: List["UploadedFile"]) -> List[Dict[str, Any]]:
    """Parse Excel files and create a structured context (similar to simple-llamaindex-analyzer)."""
    all_content: List[Dict[str, Any]] = []

    for uf in files:
        try:
            content = io.BytesIO(uf.read())
            excel_file = pd.ExcelFile(content)
            file_name = uf.name

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(content, sheet_name=sheet_name)

                context: Dict[str, Any] = {
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
            all_content.append({"file": getattr(uf, "name", "<unknown>"), "error": str(e)})

    return all_content


def create_test_analysis_prompt(data_context: List[Dict[str, Any]]) -> str:
    context_str = json.dumps(data_context, indent=2, default=str)
    prompt = f"""
You are a Senior QA Engineer analyzing Excel data specifications for comprehensive testing.

Data Context:
{context_str}

Based on this data, provide a detailed test analysis including:

## 1. TEST SCENARIOS (5+ scenarios)
For each scenario provide:
- Scenario Name
- Description
- Business Value
- Risk Level (High/Medium/Low)

## 2. TEST CASES (10+ detailed test cases)
For each test case provide:
- Test ID
- Test Name
- Objective
- Prerequisites
- Test Steps (numbered)
- Expected Results
- Test Data Required
- Priority (P1/P2/P3)

## 3. SQL VALIDATION QUERIES (5+ queries)
Provide SQL queries for:
- Data integrity checks
- Referential integrity validation
- Data quality verification
- Performance testing
- Edge case validation

## 4. DATA QUALITY CHECKS
Identify:
- Potential data quality issues
- Missing data patterns
- Data validation rules needed
- Data cleansing requirements

## 5. TEST AUTOMATION STRATEGY
Recommend:
- Which tests to automate
- Testing framework suggestions
- CI/CD integration approach
- Test data management strategy

## 6. RISK ASSESSMENT
Identify:
- Critical data risks
- Potential failure points
- Mitigation strategies

Please provide detailed, actionable recommendations specific to the data structure provided.
"""
    return prompt


def analyze_with_llm(prompt: str) -> str:
    if client is None or MODEL_NAME is None:
        raise RuntimeError("No LLM configured. Set Azure OpenAI env vars or HF_TOKEN.")
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a Senior QA Engineer expert in test design, data validation, and quality assurance. Provide detailed, practical testing strategies.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=3000,
        temperature=0.7,
    )
    return completion.choices[0].message.content


def ask_followup(data_context: List[Dict[str, Any]], question: str) -> str:
    if client is None or MODEL_NAME is None:
        return "LLM not configured."
    context_str = json.dumps(data_context, indent=2, default=str)
    follow_prompt = f"""
Data Context:
{context_str}

Question: {question}

Please provide a detailed answer based on the data context.
"""
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a QA expert. Answer questions about testing and data quality based on the provided context.",
            },
            {"role": "user", "content": follow_prompt},
        ],
        max_tokens=1000,
        temperature=0.7,
    )
    return completion.choices[0].message.content

# --------------------------- Streamlit UI ---------------------------

st.set_page_config(page_title="TestCaseGPT", page_icon="✨", layout="wide")

st.title("TestCaseGPT")
st.caption("Upload Excel files, generate QA analysis and SQL, then chat about the data.")

with st.sidebar:
    st.subheader("Model Configuration")
    st.write("Provider:", PROVIDER or "Not configured")
    st.write("Model/Deployment:", MODEL_NAME or "—")
    st.write("Endpoint:", AZURE_ENDPOINT or "https://router.huggingface.co/v1")
    if client is None:
        st.error("No LLM configured. Set Azure OpenAI env vars or HF_TOKEN in .env")

if "data_context" not in st.session_state:
    st.session_state.data_context = []
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {role, content}

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Upload Data")
    uploaded_files = st.file_uploader(
        "Drop your Excel files here (.xlsx, .xls, .csv)",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
    )
    if st.button("Analyze Files", type="primary", use_container_width=True, disabled=not uploaded_files):
        with st.spinner("Parsing files and generating analysis..."):
            parsed = parse_excel_to_context_from_uploads(uploaded_files)
            st.session_state.data_context = parsed
            try:
                prompt = create_test_analysis_prompt(parsed)
                analysis = analyze_with_llm(prompt)
                st.session_state.analysis = analysis
                st.success(f"Parsed {len(parsed)} sheet(s) across {len(uploaded_files)} file(s).")
            except Exception as e:
                st.session_state.analysis = None
                st.error(f"Error generating analysis: {e}")

    if st.session_state.data_context:
        st.markdown("### Parsed Context Summary")
        for i, ctx in enumerate(st.session_state.data_context[:6]):
            with st.expander(f"{i+1}. {ctx.get('file','?')} — {ctx.get('sheet','?')}  (rows: {ctx.get('num_rows','?')})", expanded=False):
                st.json(ctx, expanded=False)

with col_right:
    st.subheader("Analysis")
    if st.session_state.analysis:
        st.markdown(st.session_state.analysis)
    else:
        st.info("Upload files and click Analyze to generate the QA analysis and SQL suggestions.")

st.divider()

st.subheader("Chat about your data")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask a follow-up question about the uploaded data...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        if not st.session_state.data_context:
            st.warning("Please upload and analyze files first.")
        else:
            with st.spinner("Thinking..."):
                try:
                    answer = ask_followup(st.session_state.data_context, user_input)
                except Exception as e:
                    answer = f"Error: {e}"
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

st.caption("Tip: Set Azure OpenAI or HF_TOKEN in .env. To run locally: streamlit run backend/streamlit_app.py")
