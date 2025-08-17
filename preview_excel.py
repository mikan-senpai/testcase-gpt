import pandas as pd
import os

# Excel files to preview
excel_files = [
    "sample-document/Database_Specs_Sheet.xlsx",
    "sample-document/FRS_Column_Mapping_Sheet.xlsx"
]

for file_path in excel_files:
    print("=" * 60)
    print(f"FILE: {os.path.basename(file_path)}")
    print("=" * 60)

    try:
        # Read all sheets
        excel_file = pd.ExcelFile(file_path)

        for sheet_name in excel_file.sheet_names:
            print(f"\n--- Sheet: {sheet_name} ---")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"Shape: {df.shape} (rows: {len(df)}, columns: {len(df.columns)})")
            print(f"Columns: {list(df.columns)}")
            print("\nFirst 3 rows:")
            print(df.head(3).to_string())
            print()
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")

    print("\n")
