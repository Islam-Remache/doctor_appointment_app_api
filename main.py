from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db.session import get_db, engine

app = FastAPI()

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "Welcome to Doctor Appointment API"}

