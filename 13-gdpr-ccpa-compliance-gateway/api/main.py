from fastapi import FastAPI
app = FastAPI()
@app.post("/delete/{user_id}")
def delete(user_id: str): return {"status": "deleted"}