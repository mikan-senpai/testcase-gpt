import os
import pandas as pd
from openai import OpenAI, AzureOpenAI
import json
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env (search upwards and fallback to repo paths)
load_dotenv(find_dotenv(usecwd=True), override=False)
script_dir = Path(__file__).resolve().parent
load_dotenv(script_dir / ".env", override=False)
load_dotenv(script_dir.parent / ".env", override=False)

# Client initialization: Prefer Azure OpenAI if configured, else HuggingFace router
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
    # Initialize the OpenAI client with HuggingFace
    hf_api_key = os.environ.get("HF_TOKEN")
    if not hf_api_key:
        raise RuntimeError(
            "Missing configuration. Set Azure OpenAI envs (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT) or set HF_TOKEN."
        )
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=hf_api_key,
    )
    MODEL_NAME = "moonshotai/Kimi-K2-Instruct"
    print(f"Using HuggingFace Inference API | router=https://router.huggingface.co/v1 | model={MODEL_NAME}")

def read_excel_files(file_paths):
    """Read Excel files and return their content as structured text"""
    all_data = []

    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found, skipping...")
            continue

        print(f"\nReading file: {file_path}")
        file_name = Path(file_path).name

        try:
            # Read all sheets from Excel file
            excel_file = pd.ExcelFile(file_path)
            file_content = f"\n=== FILE: {file_name} ===\n"

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                file_content += f"\n--- Sheet: {sheet_name} ---\n"
                file_content += f"Columns: {', '.join(df.columns.tolist())}\n"
                file_content += f"Number of rows: {len(df)}\n\n"

                # Convert dataframe to string (first 10 rows for preview)
                if len(df) > 0:
                    preview_rows = min(10, len(df))
                    file_content += "Data Preview (first 10 rows):\n"
                    file_content += df.head(preview_rows).to_string()

                    if len(df) > 10:
                        file_content += f"\n... and {len(df) - 10} more rows\n"

                # Add summary statistics for numerical columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    file_content += "\n\nNumerical Column Statistics:\n"
                    file_content += df[numeric_cols].describe().to_string()

            all_data.append(file_content)

        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            continue

    return "\n\n".join(all_data)

def analyze_with_llm(excel_content):
    """Send Excel content to LLM for analysis"""

    prompt = f"""You are a Quality Assurance expert. Analyze the following Excel file data and provide:

1. TEST SCENARIOS: High-level testing scenarios based on the data structure and content
2. TEST CASES: Detailed test cases with steps, expected results, and test data
3. SQL QUERIES: Relevant SQL queries for data validation and testing
4. DATA QUALITY CHECKS: Identify potential data quality issues and validation rules

Excel Data:
{excel_content}

Please provide a comprehensive analysis with:
- At least 5 test scenarios
- At least 10 detailed test cases
- At least 5 SQL queries for data validation
- Data quality recommendations

Format your response in a clear, structured manner with proper headings and numbering."""

    try:
        print("\nSending data to LLM for analysis...")
        print("This may take a moment...")

        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a QA expert who creates comprehensive test documentation based on data analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Error calling LLM: {str(e)}")
        return None

def save_results(analysis, output_file="test_analysis_output.md"):
    """Save the analysis results to a markdown file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Excel Data Test Analysis Report\n\n")
            f.write("Generated using AI Analysis\n\n")
            f.write("---\n\n")
            f.write(analysis)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"Error saving results: {str(e)}")

def main():
    """Main function to run the Excel analysis"""

    # Define the Excel files to analyze
    # Using the actual Excel files from sample-document folder
    excel_files = [
        "sample-document/Database_Specs_Sheet.xlsx",
        "sample-document/FRS_Column_Mapping_Sheet.xlsx"
    ]

    print("=" * 60)
    print("EXCEL FILE ANALYZER WITH LLM")
    print("=" * 60)

    # Check if files exist
    existing_files = []
    for file in excel_files:
        if os.path.exists(file):
            existing_files.append(file)
            print(f"✓ Found: {file}")
        else:
            print(f"✗ Not found: {file}")

    if not existing_files:
        print("\n⚠ No Excel files found. Please update the file paths in the script.")
        print("\nTo use this script:")
        print("1. Place your Excel files in the same directory as this script")
        print("2. Update the 'excel_files' list with your file names")
        print("3. Run the script again")
        return

    # Read Excel files
    excel_content = read_excel_files(existing_files)

    if not excel_content:
        print("No data could be read from the Excel files.")
        return

    # Analyze with LLM
    analysis = analyze_with_llm(excel_content)

    if analysis:
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        print(analysis)

        # Save results to file
        save_results(analysis)
    else:
        print("Failed to get analysis from LLM.")

if __name__ == "__main__":
    main()
