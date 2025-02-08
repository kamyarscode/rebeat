from fastapi import FastAPI, Depends, HTTPException, Form
import uvicorn

app = FastAPI()

# Root route
@app.get("/")
async def root():

    return {"message": "Hello World!"}

# login endpoint, change to post later.
@app.get("/login")
def login():

    return {"message": "Login reached"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
