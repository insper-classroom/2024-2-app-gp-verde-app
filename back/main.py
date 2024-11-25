from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pickle

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

class ModelInput(BaseModel):
    feature: float

@app.get("/")
def read_root():
    return {"message": "API do modelo está funcionando!"}

@app.post("/predict/")
def predict(input_data: ModelInput):
    prediction = model.predict([[input_data.feature]])
    return {"prediction": prediction[0]}
