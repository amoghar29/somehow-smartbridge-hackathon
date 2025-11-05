"""
Minimal test server to verify FastAPI is working
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Test server running"}

if __name__ == "__main__":
    print("Starting minimal test server...")
    print("Visit: http://127.0.0.1:8000/")
    uvicorn.run(app, host="127.0.0.1", port=8000)
