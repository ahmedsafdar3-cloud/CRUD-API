from fastapi import FastAPI

app = FastAPI(title="Task API")


@app.get("/")
def hello():
    return {"message": "Hello, world!"}
