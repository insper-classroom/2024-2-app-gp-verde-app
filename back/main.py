from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import keras

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


model = keras.saving.load_model("model/model_artigo.keras")

def preprocess_txt(file_content: str):
    data = np.array([len(file_content)])  
    return data

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        return {"error": "Por favor, envie um arquivo .txt"}

    content = await file.read()
    content = content.decode("utf-8")

    input_data = preprocess_txt(content)
    prediction = model.predict(np.array([input_data]))

    return {"prediction": prediction.tolist()}
