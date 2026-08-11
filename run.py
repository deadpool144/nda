import uvicorn
import os

if __name__ == "__main__":
    print("Starting LexForge Contract Creator Platform...")
    print("Navigate to http://localhost:8000 in your browser.")
    # Ensure port is open and start uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
