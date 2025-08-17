"""
Excel Document Analyzer using LlamaIndex and LlamaParse
This script parses Excel files and generates test scenarios, test cases, and queries
"""

import os
from pathlib import Path
from typing import List
import pandas as pd
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env (search upwards and fallback to repo paths)
load_dotenv(find_dotenv(usecwd=True), override=False)
script_dir = Path(__file__).resolve().parent
load_dotenv(script_dir / ".env", override=False)
load_dotenv(script_dir.parent / ".env", override=False)

# LlamaIndex imports
from llama_index.core import (
    Document,
    VectorStoreIndex,
    SimpleDirectoryReader,
    ServiceContext,
    StorageContext,
    load_index_from_storage
)
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.indices.struct_store import PandasIndex
from llama_index.core.schema import TextNode
from llama_index.readers.file import PandasExcelReader
from llama_index.core.prompts import PromptTemplate

# For using HuggingFace models with LlamaIndex
from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

class ExcelDocumentAnalyzer:
    def __init__(self, hf_token=None):
        """Initialize the analyzer with HuggingFace token"""
        self.hf_token = hf_token or os.environ.get("HF_TOKEN")
        if not self.hf_token:
            raise RuntimeError("HF_TOKEN is not set. Please set it in your environment or in a .env file.")
        self.documents = []
        self.index = None
        self.setup_llm()

    def setup_llm(self):
        """Setup LLM configuration for LlamaIndex"""
        # Use HuggingFace Inference API with the working model
        self.llm = HuggingFaceInferenceAPI(
            model_name="moonshotai/Kimi-K2-Instruct",
            token=self.hf_token,
            task="text-generation",
            device=-1,
            # Additional parameters
            model_kwargs={
                "temperature": 0.7,
                "max_new_tokens": 2000,
            }
        )

        # Ensure cache folder exists
        cache_dir = Path("./cache")
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Use HuggingFace embeddings
        self.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_folder=str(cache_dir)
        )

    def parse_excel_with_pandas(self, file_path: str) -> List[Document]:
        """Parse Excel file using Pandas and convert to LlamaIndex Documents"""
        documents = []
        file_name = Path(file_path).name

        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # Create structured content
                content = f"File: {file_name}\n"
                content += f"Sheet: {sheet_name}\n"
                content += f"Columns: {', '.join(df.columns.tolist())}\n"
                content += f"Number of rows: {len(df)}\n\n"

                # Add data preview
                content += "Data Sample:\n"
                content += df.head(10).to_string()

                # Add statistics for numerical columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    content += "\n\nStatistics:\n"
                    content += df[numeric_cols].describe().to_string()

                # Create metadata
                metadata = {
                    "file_name": file_name,
                    "sheet_name": sheet_name,
                    "num_rows": len(df),
                    "num_columns": len(df.columns),
                    "columns": df.columns.tolist()
                }

                # Create LlamaIndex Document
                doc = Document(
                    text=content,
                    metadata=metadata
                )
                documents.append(doc)

        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")

        return documents

    def load_excel_documents(self, file_paths: List[str]):
        """Load multiple Excel files"""
        print("Loading Excel documents...")

        for file_path in file_paths:
            if os.path.exists(file_path):
                print(f"  Parsing: {file_path}")
                docs = self.parse_excel_with_pandas(file_path)
                self.documents.extend(docs)
            else:
                print(f"  File not found: {file_path}")

        print(f"Loaded {len(self.documents)} document chunks")

    def build_index(self):
        """Build vector index from documents"""
        if not self.documents:
            print("No documents to index!")
            return

        print("Building index...")

        # Create service context with our LLM and embedding model
        from llama_index.core import Settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = 1024

        # Build the index
        self.index = VectorStoreIndex.from_documents(
            self.documents,
            show_progress=True
        )

        print("Index built successfully!")

    def generate_test_analysis(self) -> str:
        """Generate comprehensive test analysis using the index"""
        if not self.index:
            print("No index available. Please build index first.")
            return None

        # Create query engine
        query_engine = self.index.as_query_engine(
            response_mode="tree_summarize",
            verbose=True
        )

        # Define comprehensive analysis prompt
        analysis_prompt = """
        Based on the Excel data provided, perform a comprehensive QA analysis:

        1. TEST SCENARIOS (provide at least 5):
           - Describe high-level testing scenarios
           - Include functional and data validation scenarios
           - Consider edge cases and boundary conditions

        2. TEST CASES (provide at least 10 detailed test cases):
           - Test Case ID
           - Description
           - Prerequisites
           - Test Steps
           - Expected Results
           - Test Data

        3. SQL QUERIES (provide at least 5):
           - Data validation queries
           - Data integrity checks
           - Performance testing queries
           - Data quality verification queries

        4. DATA QUALITY CHECKS:
           - Identify potential data issues
           - Suggest validation rules
           - Recommend data cleansing strategies
           - Highlight missing or inconsistent data patterns

        5. AUTOMATION RECOMMENDATIONS:
           - Suggest which tests should be automated
           - Recommend testing tools
           - Provide automation framework suggestions

        Please analyze the data thoroughly and provide detailed, actionable recommendations.
        """

        print("\nGenerating test analysis...")
        print("This may take a moment...\n")

        try:
            response = query_engine.query(analysis_prompt)
            return str(response)
        except Exception as e:
            print(f"Error generating analysis: {str(e)}")
            return None

    def query_specific(self, question: str) -> str:
        """Query specific information from the documents"""
        if not self.index:
            print("No index available. Please build index first.")
            return None

        query_engine = self.index.as_query_engine()
        response = query_engine.query(question)
        return str(response)

    def save_analysis(self, analysis: str, output_file: str = "llamaindex_test_analysis.md"):
        """Save analysis results to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# Excel Data Test Analysis Report\n")
                f.write("## Generated using LlamaIndex and LlamaParse\n\n")
                f.write("---\n\n")
                f.write(analysis)
            print(f"\n✅ Results saved to: {output_file}")
        except Exception as e:
            print(f"Error saving results: {str(e)}")


def main():
    """Main function to run the analysis"""

    print("=" * 60)
    print("EXCEL ANALYZER WITH LLAMAINDEX")
    print("=" * 60)

    # Excel files to analyze
    excel_files = [
        "sample-document/Database_Specs_Sheet.xlsx",
        "sample-document/FRS_Column_Mapping_Sheet.xlsx"
    ]

    # Initialize analyzer
    analyzer = ExcelDocumentAnalyzer()

    # Load documents
    analyzer.load_excel_documents(excel_files)

    if not analyzer.documents:
        print("No documents loaded. Exiting.")
        return

    # Build index
    analyzer.build_index()

    # Generate comprehensive analysis
    analysis = analyzer.generate_test_analysis()

    if analysis:
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        print(analysis)

        # Save to file
        analyzer.save_analysis(analysis)

        # Interactive query mode
        print("\n" + "=" * 60)
        print("INTERACTIVE QUERY MODE")
        print("=" * 60)
        print("You can now ask specific questions about the data.")
        print("Type 'quit' to exit.\n")

        while True:
            question = input("Your question: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break

            if question:
                response = analyzer.query_specific(question)
                print(f"\nAnswer: {response}\n")
    else:
        print("Failed to generate analysis.")

    print("\n✨ Analysis complete!")


if __name__ == "__main__":
    main()
