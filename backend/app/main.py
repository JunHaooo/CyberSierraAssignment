from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.utils import allowed_file, save_file, read_file_top_n, query_file
from app.schemas import TopRowsRequest, TopRowsResponse
from app.models import UploadFileResponse, QueryRequest, QueryResponse
import os

app = FastAPI(title="AI Excel/CSV Query App")

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    # Save file
    with open(filepath, "wb") as f:
        f.write(await file.read())
    # Return JSON response
    return JSONResponse({"success": True, "filename": file.filename})

@app.post("/top_rows", response_model=TopRowsResponse)
async def top_rows(request: TopRowsRequest):
    try:
        df = read_file_top_n(
            filepath=f"uploads/{request.filename}",
            sheet_name=request.sheet_name,
            n=request.n
        )
        return {"columns": df.columns.tolist(), "rows": df.values.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_csv(request: QueryRequest):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, request.filename)
        
        # Pass request.sheet_name here! 
        # (Make sure your QueryRequest model in app.models has sheet_name: str = None)
        answer = query_file(filepath, request.query, sheet_name=request.sheet_name)
        
        if answer is None:
            return {"answer": "I'm sorry, I couldn't process that data query."}
            
        return {"answer": str(answer)}
        
    except Exception as e:
        print("CRITICAL BACKEND ERROR:", e)
        raise HTTPException(status_code=500, detail={"error": str(e)})