# 📊 Excel Document Test Analyzer with AI

An intelligent test analysis tool that uses AI/LLM to analyze Excel documents and generate comprehensive test scenarios, test cases, SQL queries, and quality assurance documentation.

## 🎯 Features

- **Automated Test Generation**: Generates test scenarios and detailed test cases from Excel data
- **SQL Query Generation**: Creates validation queries for data testing
- **Data Quality Analysis**: Identifies potential data issues and validation rules
- **Interactive Q&A**: Ask specific questions about your data and testing strategies
- **Multiple Analysis Approaches**: Choose from simple to advanced analysis methods
- **Works Behind Corporate Firewalls**: Configured for enterprise environments

## 📁 Project Structure

```
python-codes/
├── simple-llamaindex-analyzer.py   # ⭐ Recommended - Minimal dependencies
├── excel-analyzer-llm.py          # Basic analyzer with direct LLM calls
├── llamaindex-excel-analyzer.py   # Advanced with vector indexing
├── preview_excel.py               # Quick Excel file preview
├── hugging-llm.py                # Test HuggingFace API connection
├── requirements-minimal.txt       # Essential packages only
├── requirements-all.txt          # All packages for full features
└── README.md                     # This file

sample-document/
├── Database_Specs_Sheet.xlsx     # Sample database specifications
└── FRS_Column_Mapping_Sheet.xlsx # Sample column mapping document
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Excel files to analyze

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd C:\botcase\only-ui\botcase-only-ui\python-codes
```

2. **Install minimal requirements (recommended):**
```bash
pip install -r requirements-minimal.txt
```

Or install manually:
```bash
pip install pandas openpyxl openai requests
```

### Basic Usage

1. **Preview your Excel files (optional):**
```bash
python preview_excel.py
```

2. **Run the analyzer:**
```bash
python simple-llamaindex-analyzer.py
```

3. **Check the output:**
- Results will be displayed in the console
- Saved to `simple_test_analysis.md`
- Interactive mode will start for Q&A

## 📝 Script Descriptions

### `simple-llamaindex-analyzer.py` ⭐ (Recommended)

The main analyzer with minimal dependencies. Best for most use cases.

**Features:**
- Parses Excel structure and data
- Generates 5+ test scenarios
- Creates 10+ detailed test cases
- Produces SQL validation queries
- Provides data quality recommendations
- Interactive Q&A mode

**Usage:**
```bash
python simple-llamaindex-analyzer.py
```

**Output:** `simple_test_analysis.md`

### `excel-analyzer-llm.py`

Basic analyzer with straightforward LLM integration.

**Usage:**
```bash
python excel-analyzer-llm.py
```

**Output:** `test_analysis_output.md`

### `llamaindex-excel-analyzer.py`

Advanced analyzer with vector indexing and document chunking.

**Requirements:**
```bash
pip install -r requirements-all.txt
```

**Usage:**
```bash
python llamaindex-excel-analyzer.py
```

**Output:** `llamaindex_test_analysis.md`

### `preview_excel.py`

Quick preview tool to understand your Excel data structure.

**Usage:**
```bash
python preview_excel.py
```

Shows:
- Sheet names
- Column names and types
- Row counts
- First 3 rows of data

### `hugging-llm.py`

Test script to verify HuggingFace API connectivity.

**Usage:**
```bash
python hugging-llm.py
```

## 📊 Input Files

Place your Excel files in the `sample-document` folder or update the file paths in the scripts.

**Default files:**
- `../sample-document/Database_Specs_Sheet.xlsx`
- `../sample-document/FRS_Column_Mapping_Sheet.xlsx`

To use different files, edit the `excel_files` list in the script:
```python
excel_files = [
    "path/to/your/file1.xlsx",
    "path/to/your/file2.xlsx"
]
```

## 📤 Output Format

The analyzer generates a comprehensive markdown report including:

### 1. Test Scenarios
- High-level testing strategies
- Business value assessment
- Risk levels (High/Medium/Low)

### 2. Test Cases
- Test ID and name
- Objectives and prerequisites
- Step-by-step procedures
- Expected results
- Required test data
- Priority levels (P1/P2/P3)

### 3. SQL Validation Queries
- Data integrity checks
- Referential integrity validation
- Performance testing queries
- Data quality verification

### 4. Data Quality Analysis
- Potential data issues
- Validation rules
- Data cleansing recommendations
- Missing data patterns

### 5. Test Automation Strategy
- Automation recommendations
- Framework suggestions
- CI/CD integration approach

### 6. Risk Assessment
- Critical data risks
- Potential failure points
- Mitigation strategies

## 🔧 Configuration

### API Token

The scripts use HuggingFace API with a default token. To use your own:

1. **Set environment variable:**
```bash
set HF_TOKEN=your_token_here  # Windows
export HF_TOKEN=your_token_here  # Linux/Mac
```

2. **Or edit in script:**
```python
api_key = "your_token_here"
```

### Model Selection

Default model: `moonshotai/Kimi-K2-Instruct`

To change the model, edit:
```python
model="your-preferred-model"
```

## 🐛 Troubleshooting

### SSL Certificate Error
```python
SSL: CERTIFICATE_VERIFY_FAILED
```
**Solution:** The scripts include SSL bypass for corporate environments.

### Model Not Available
```python
The requested model is not supported
```
**Solution:** The script will try alternative models automatically.

### File Not Found
```python
File not found: sample1.xlsx
```
**Solution:** Update file paths in the script or place files in the correct directory.

### Module Not Found
```python
ModuleNotFoundError: No module named 'pandas'
```
**Solution:** Install requirements:
```bash
pip install -r requirements-minimal.txt
```

## 💡 Interactive Mode

After analysis, you can ask questions like:
- "Generate test cases for data migration"
- "What SQL queries would verify foreign keys?"
- "Suggest boundary value test cases"
- "Identify risks in column mapping"

Type `quit` to exit interactive mode.

## 📦 Installation Options

### Minimal (50MB) - Recommended
```bash
pip install pandas openpyxl openai requests
```

### Standard (500MB) - With HuggingFace
```bash
pip install pandas openpyxl openai requests transformers
```

### Full (1GB+) - All features
```bash
pip install -r requirements-all.txt
```

## 🏢 Corporate Environment Setup

If running behind a corporate firewall:

1. **Proxy Configuration:**
```python
os.environ['HTTP_PROXY'] = 'http://your-proxy:port'
os.environ['HTTPS_PROXY'] = 'http://your-proxy:port'
```

2. **SSL Issues:**
The scripts include SSL verification bypass for development.

3. **Offline Mode:**
Consider using local models with Ollama or similar solutions.

## 📈 Performance Tips

1. **Large Excel Files:** The analyzer handles files up to 10,000 rows efficiently
2. **Multiple Sheets:** All sheets are processed automatically
3. **Memory Usage:** Minimal mode uses <500MB RAM
4. **Processing Time:** Typically 30-60 seconds per analysis

## 🤝 Contributing

To add new features or improve the analyzer:

1. Add new test patterns in the prompt
2. Extend data parsing capabilities
3. Add support for more file formats
4. Improve error handling

## 📄 License

This project is for internal use. Please follow your organization's guidelines for AI tool usage.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the error messages in console
3. Ensure all dependencies are installed
4. Verify Excel file formats are correct

## 🎉 Examples

### Example Command Sequence
```bash
# Navigate to project
cd C:\botcase\only-ui\botcase-only-ui\python-codes

# Install dependencies
pip install -r requirements-minimal.txt

# Preview data
python preview_excel.py

# Run analysis
python simple-llamaindex-analyzer.py

# View results
type simple_test_analysis.md
```

### Example Interactive Query
```
Your question: Generate test cases for null value handling
Answer: Based on the data structure, here are test cases for null handling...
```

## 🔮 Future Enhancements

- [ ] Support for CSV files
- [ ] Support for JSON data
- [ ] Web-based UI interface
- [ ] Batch processing multiple files
- [ ] Export to JIRA/TestRail
- [ ] Automated test execution
- [ ] Performance benchmarking
- [ ] Custom test templates

---

**Note:** This tool is designed to assist QA engineers in generating comprehensive test documentation. Always review and validate the generated tests before implementation.

**Version:** 1.0.0
**Last Updated:** December 2024
**Tested With:** Python 3.10, Windows 10/11
# testcase-gpt
