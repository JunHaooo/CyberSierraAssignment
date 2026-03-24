import os
import re
import pandas as pd
from dotenv import load_dotenv
from pandasai import SmartDataframe 
from pandasai_litellm.litellm import LiteLLM
from app.config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize LLM
llm = LiteLLM(model="gpt-4o-mini", api_key=api_key)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """Save uploaded file to UPLOAD_FOLDER."""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    # Using 'with' is safer for file writing
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    return filepath

def read_file_top_n(filepath: str, n: int, sheet_name: str = None):
    ext = os.path.splitext(filepath)[-1].lower()
    
    if ext in ['.csv']:
        # CSVs ignore the sheet_name entirely
        return pd.read_csv(filepath, nrows=n)
    
    elif ext in ['.xlsx', '.xls']:
        # Excel needs the sheet_name
        return pd.read_excel(filepath, sheet_name=sheet_name, nrows=n)
    
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def query_file(filepath, query, sheet_name=None):
    """Run an AI query using SmartDataframe logic."""
    ext = filepath.rsplit('.', 1)[1].lower()

    try:
        # 1. Load data
        if ext == "csv":
            df_pandas = pd.read_csv(filepath)
        else:
            df_pandas = pd.read_excel(filepath, sheet_name=sheet_name)

        # 2. Sanitize Name (Fixes the Pydantic 'lowercase and underscores' error)
        base_name = os.path.basename(filepath).rsplit('.', 1)[0]
        sheet_suffix = str(sheet_name) if sheet_name else "data"
        combined = f"{base_name}_{sheet_suffix}"
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', combined).lower()
        clean_name = re.sub(r'_+', '_', clean_name).strip('_')

        # 3. Create SmartDataframe
        sdf = SmartDataframe(
            df_pandas, 
            name=clean_name, 
            config={"llm": llm}
        )

        # 4. Get Response
        response = sdf.chat(query)
        return str(response) if response is not None else "No answer found."

    except Exception as e:
        print(f"Query Error: {e}")
        return f"Error: {str(e)}"