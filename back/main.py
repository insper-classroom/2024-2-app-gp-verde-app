from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import tensorflow as tf
from utils import *
import numpy as np
from plot import *
import pickle
import os

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

TEMP_DIR = "./uploads/coverage"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/generate-heatmap")
async def generate_heatmap(file: UploadFile = File(...)):
    try:
        cov_file = os.path.join(TEMP_DIR, file.filename)
        with open(cov_file, "wb") as f:
            f.write(await file.read())
        max_size = 3500000
        min_size = 2500000
        step = 100
        sample = os.path.basename(cov_file).split("_")[0]
        corrected_df = pd.read_csv(cov_file, sep="\t")
        smoothed_cov = smooth_normalized_coverage(corrected_df, chr_arms, min_size, max_size, step)
        cov_matrix = create_2d_array(smoothed_cov)
        z_scored_matrix = z_score_transform(cov_matrix)
        heatmap_buffer = plot_heatmap(z_scored_matrix, sample)
        os.remove(cov_file)
        return StreamingResponse(heatmap_buffer, media_type="image/png")
    except Exception as e:
        if os.path.exists(cov_file):
            os.remove(cov_file)
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}")