from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tensorflow as tf
from utils import *
import numpy as np
from plot import *
import base64 
import pickle
import os
import shutil

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = tf.keras.models.load_model("model/model_artigo_v4.keras")

with open("./data/arm_lengths/arm_lengths.pkl", "rb") as f:
    chr_arms = pickle.load(f)

TEMP_DIR = "./uploads/coverage"
LOG_DIR = "./logs"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/process-multiple-files")
async def process_multiple_files(files: list[UploadFile] = File(...)):
    results = []
    threshold = 0.6518086791038513  # Limiar para classificação
    try:
        for file in files:
            # Salvar arquivo temporariamente
            cov_file = os.path.join(TEMP_DIR, file.filename)
            with open(cov_file, "wb") as f:
                f.write(await file.read())

            try:
                # Criar pasta para logs deste arquivo
                log_subdir = os.path.join(LOG_DIR, os.path.splitext(file.filename)[0])
                os.makedirs(log_subdir, exist_ok=True)

                # Copiar o arquivo enviado para a pasta de logs
                shutil.copy(cov_file, os.path.join(log_subdir, file.filename))

                # Pré-processamento
                min_size = 2500000
                max_size = 3500000
                step = 100

                # Processar arquivo de cobertura para matriz de entrada
                cov_matrix = process_new_sample(cov_file, chr_arms, min_size, max_size, step)

                # Preparar a matriz para predição
                prepared_matrix = prepare_data([cov_matrix])[0]

                # Predição
                prediction = model.predict(np.array([prepared_matrix]))[0][0]
                prediction_result = "Positive" if prediction >= threshold else "Negative"

                # Gerar heatmap
                corrected_df = pd.read_csv(cov_file, sep="\t")
                smoothed_cov = smooth_normalized_coverage(corrected_df, chr_arms, min_size, max_size, step)
                cov_matrix = create_2d_array(smoothed_cov)
                heatmap_buffer = plot_heatmap(cov_matrix, file.filename.split('.')[0])

                # Salvar heatmap na pasta de logs
                heatmap_path = os.path.join(log_subdir, f"{os.path.splitext(file.filename)[0]}_heatmap.png")
                with open(heatmap_path, "wb") as heatmap_file:
                    heatmap_buffer.seek(0)
                    heatmap_file.write(heatmap_buffer.read())

                # Converter heatmap para Base64
                heatmap_buffer.seek(0)
                heatmap_base64 = base64.b64encode(heatmap_buffer.read()).decode("utf-8")

                # Adicionar resultado ao retorno
                results.append({
                    "filename": file.filename,
                    "prediction": prediction_result,
                    "heatmap": heatmap_base64,
                })
            finally:
                # Remover arquivo temporário
                os.remove(cov_file)

        # Retornar resultados
        return JSONResponse(content={"results": results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivos: {str(e)}")
