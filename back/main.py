from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
from utils import *
from plot import *
import numpy as np
import pickle

app = FastAPI()

origins = ["http://localhost:5173"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = tf.keras.models.load_model("model/model_artigo.keras")

with open("./data/arm_lengths/arm_lengths.pkl", "rb") as f:
    chr_arms = pickle.load(f)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        
        min_size = 2500000
        max_size = 3500000
        step = 100
        
        from io import StringIO
        file_stream = StringIO(file_content.decode("utf-8"))
        cov_matrix = process_new_sample(file_stream, chr_arms, min_size, max_size, step)

        cov_matrix_expanded = np.expand_dims(cov_matrix, axis=-1)
        
        prediction = model.predict(np.array([cov_matrix_expanded]))
        
        return {"prediction": float(prediction[0][0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}")
