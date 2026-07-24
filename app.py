import os
import shutil
import tempfile
import zipfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from src.converter import UnstructuredConverter
from src.converter.exporter import Exporter

app = FastAPI(
    title="Unstructured File Converter Web API",
    description="API to convert unstructured documents (PDF, DOCX, HTML, TXT, CSV, Images) into Markdown and JSON AST.",
    version="1.0.0"
)

# Ensure output and static directories exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

converter = UnstructuredConverter()

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Unstructured Converter API</h1><p>Static index.html not found.</p>"

@app.post("/api/convert")
async def convert_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_input_path = os.path.join(tmp_dir, file.filename)
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            md_path, json_path, doc_model = converter.convert_file(temp_input_path, OUTPUT_DIR)
            
            with open(md_path, "r", encoding="utf-8") as mf:
                md_content = mf.read()

            with open(json_path, "r", encoding="utf-8") as jf:
                json_content = jf.read()

            return {
                "status": "success",
                "filename": file.filename,
                "title": doc_model.title,
                "metadata": doc_model.metadata.model_dump(),
                "markdown": md_content,
                "json": json_content,
                "download_md_url": f"/api/download?file={os.path.basename(md_path)}",
                "download_json_url": f"/api/download?file={os.path.basename(json_path)}"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")

@app.post("/api/convert-batch")
async def convert_batch_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    results = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        for file in files:
            temp_input_path = os.path.join(tmp_dir, file.filename)
            with open(temp_input_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            try:
                md_path, json_path, doc_model = converter.convert_file(temp_input_path, OUTPUT_DIR)
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "word_count": doc_model.metadata.word_count,
                    "md_file": os.path.basename(md_path),
                    "json_file": os.path.basename(json_path)
                })
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })

    return {"results": results}

@app.get("/api/download")
async def download_file(file: str):
    safe_filename = os.path.basename(file)
    target_path = os.path.join(OUTPUT_DIR, safe_filename)
    if os.path.exists(target_path):
        return FileResponse(target_path, filename=safe_filename)
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Unstructured Converter Web UI server at http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
