from fastapi import FastAPI

app = FastAPI(title="MindFlow AI")

@app.get("/")
def root():
    return {"message": "Xin chào! MindFlow đang hoạt động 🧠✨"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "project": "MindFlow - Mental Health AI"}