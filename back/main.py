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

# Inicializa a aplicação FastAPI
app = FastAPI()

# Configuração de CORS para permitir requisições de qualquer origem
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir todas as origens
    allow_credentials=True,
    allow_methods=["*"],    # Permitir todos os métodos HTTP
    allow_headers=["*"],    # Permitir todos os cabeçalhos
)

# Carregamento do modelo pré-treinado de TensorFlow
model = tf.keras.models.load_model("model/model_artigo_v4.keras")

# Carregamento das informações de comprimento dos braços cromossômicos
with open("./data/arm_lengths/arm_lengths.pkl", "rb") as f:
    chr_arms = pickle.load(f)

# Definição de diretórios para uploads e logs
TEMP_DIR = "./uploads/coverage"
LOG_DIR = "./logs"
os.makedirs(TEMP_DIR, exist_ok=True)  # Garante que o diretório temporário existe
os.makedirs(LOG_DIR, exist_ok=True)  # Garante que o diretório de logs existe

# Endpoint raiz para verificação da API
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Endpoint para processar múltiplos arquivos enviados pelo usuário
@app.post("/process-multiple-files")
async def process_multiple_files(files: list[UploadFile] = File(...)):
    """
    Processa múltiplos arquivos de cobertura enviados pelo usuário.
    Para cada arquivo:
    1. Salva temporariamente.
    2. Pré-processa os dados e realiza predição.
    3. Gera um heatmap e salva nos logs.
    4. Retorna resultados, incluindo as predições e o heatmap em Base64.
    """
    results = []
    threshold = 0.6518086791038513  # Limiar para classificação

    try:
        for file in files:
            # Salvar o arquivo temporariamente
            cov_file = os.path.join(TEMP_DIR, file.filename)
            with open(cov_file, "wb") as f:
                f.write(await file.read())  # Escreve o conteúdo do arquivo

            try:
                # Criar subdiretório para logs deste arquivo
                log_subdir = os.path.join(LOG_DIR, os.path.splitext(file.filename)[0])
                os.makedirs(log_subdir, exist_ok=True)

                # Copiar o arquivo enviado para os logs
                shutil.copy(cov_file, os.path.join(log_subdir, file.filename))

                # Pré-processamento do arquivo
                min_size = 2500000
                max_size = 3500000
                step = 100
                cov_matrix = process_new_sample(cov_file, chr_arms, min_size, max_size, step)

                # Preparar matriz para predição
                prepared_matrix = prepare_data([cov_matrix])[0]

                # Realizar predição com o modelo
                prediction = model.predict(np.array([prepared_matrix]))[0][0]
                prediction_result = "Positive" if prediction >= threshold else "Negative"

                # Gerar heatmap do arquivo
                corrected_df = pd.read_csv(cov_file, sep="\t")
                smoothed_cov = smooth_normalized_coverage(corrected_df, chr_arms, min_size, max_size, step)
                cov_matrix = create_2d_array(smoothed_cov)
                heatmap_buffer = plot_heatmap(cov_matrix, file.filename.split('.')[0])

                # Salvar heatmap nos logs
                heatmap_path = os.path.join(log_subdir, f"{os.path.splitext(file.filename)[0]}_heatmap.png")
                with open(heatmap_path, "wb") as heatmap_file:
                    heatmap_buffer.seek(0)
                    heatmap_file.write(heatmap_buffer.read())

                # Converter heatmap para Base64
                heatmap_buffer.seek(0)
                heatmap_base64 = base64.b64encode(heatmap_buffer.read()).decode("utf-8")

                # Adicionar resultados ao retorno
                results.append({
                    "filename": file.filename,
                    "prediction": prediction_result,
                    "heatmap": heatmap_base64,
                })
            finally:
                # Remover o arquivo temporário
                os.remove(cov_file)

        # Retornar todos os resultados
        return JSONResponse(content={"results": results})
    except Exception as e:
        # Em caso de erro, retornar uma exceção HTTP
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivos: {str(e)}")
