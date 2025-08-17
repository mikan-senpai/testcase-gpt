"""
Simplified Excel Analyzer using LlamaIndex
Works with minimal dependencies and the working HuggingFace API
"""

import os
import pandas as pd
from openai import OpenAI, AzureOpenAI
import json
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

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

if AZURE_ENDPOINT and AZURE_API_KEY and AZURE_DEPLOYMENT:
    client = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
    )
    MODEL_NAME = AZURE_DEPLOYMENT
    print(f"Using Azure OpenAI | endpoint={AZURE_ENDPOINT} | deployment={AZURE_DEPLOYMENT} | api_version={AZURE_API_VERSION}")
else:
    HF_TOKEN = os.environ.get("HF_TOKEN")
    if not HF_TOKEN:
        raise RuntimeError(
            "Missing configuration. Set Azure OpenAI envs (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT) or set HF_TOKEN."
        )
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )
    MODEL_NAME = "openai/gpt-oss-20b:fireworks-ai"
    print(f"Using HuggingFace Inference API | router=https://router.huggingface.co/v1 | model={MODEL_NAME}")

def parse_excel_to_context(file_paths):
    """Parse Excel files and create a structured context"""
    all_content = []

    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        print(f"Parsing: {file_path}")
        file_name = os.path.basename(file_path)

        try:
            # Read Excel file
            excel_file = pd.ExcelFile(file_path)

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # Build context
                context = {
                    "file": file_name,
                    "sheet": sheet_name,
                    "columns": df.columns.tolist(),
                    "num_rows": len(df),
                    "sample_data": df.head(5).to_dict(),
                    "data_types": df.dtypes.astype(str).to_dict(),
                    "null_counts": df.isnull().sum().to_dict(),
                    "unique_counts": {col: df[col].nunique() for col in df.columns}
                }

                # Add statistics for numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    context["statistics"] = df[numeric_cols].describe().to_dict()

                all_content.append(context)

        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")

    return all_content

def create_test_analysis_prompt(data_context):
    """Create a comprehensive prompt for test analysis"""

    # Convert context to readable format
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

def analyze_with_llm(prompt):
    """Send prompt to LLM for analysis"""
    try:
        print("\nGenerating comprehensive test analysis...")
        print("This may take a moment...\n")

        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Senior QA Engineer expert in test design, data validation, and quality assurance. Provide detailed, practical testing strategies."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=3000,
            temperature=0.7
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Error calling LLM: {str(e)}")
        return None

def interactive_query(data_context):
    """Allow interactive queries about the data"""
    context_str = json.dumps(data_context, indent=2, default=str)

    print("\n" + "=" * 60)
    print("INTERACTIVE QUERY MODE")
    print("=" * 60)
    print("Ask specific questions about the data or testing strategies.")
    print("Type 'quit' to exit.\n")

    while True:
        question = input("Your question: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break

        if question:
            try:
                prompt = f"""
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
                            "content": "You are a QA expert. Answer questions about testing and data quality based on the provided context."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )

                print(f"\nAnswer: {completion.choices[0].message.content}\n")

            except Exception as e:
                print(f"Error: {str(e)}\n")

def save_results(analysis, output_file="simple_test_analysis.md"):
    """Save analysis to markdown file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Excel Data Test Analysis Report\n")
            f.write("## Generated using LlamaIndex Approach with HuggingFace\n\n")
            f.write("---\n\n")
            f.write(analysis)
        print(f"\n✅ Results saved to: {output_file}")
    except Exception as e:
        print(f"Error saving results: {str(e)}")

def main():
    """Main execution function"""

    print("=" * 60)
    print("SIMPLIFIED EXCEL ANALYZER")
    print("Using LlamaIndex approach with minimal dependencies")
    print("=" * 60)

    # Excel files to analyze
    excel_files = [
        "sample-document/Database_Specs_Sheet.xlsx",
        "sample-document/FRS_Column_Mapping_Sheet.xlsx"
    ]

    # Parse Excel files
    data_context = parse_excel_to_context(excel_files)

    if not data_context:
        print("No data could be parsed. Please check your Excel files.")
        return

    print(f"\n✅ Successfully parsed {len(data_context)} sheets")

    # Create analysis prompt
    prompt = create_test_analysis_prompt(data_context)

    # Generate analysis
    analysis = analyze_with_llm(prompt)

    if analysis:
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        print(analysis)

        # Save results
        save_results(analysis)

        # Interactive mode
        interactive_query(data_context)
    else:
        print("Failed to generate analysis.")

    print("\n✨ Analysis complete!")

if __name__ == "__main__":
    main()
