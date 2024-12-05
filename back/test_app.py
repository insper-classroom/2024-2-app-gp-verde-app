import os
import pytest
from fastapi.testclient import TestClient
from main import app  # Substitua por onde está definida sua aplicação FastAPI

# Inicializa o cliente de teste
client = TestClient(app)

# Diretório de teste temporário
TEST_DIR = "./test_files"
os.makedirs(TEST_DIR, exist_ok=True)

# Função para criar um arquivo de teste
def create_test_file(filename, content):
    filepath = os.path.join(TEST_DIR, filename)
    with open(filepath, "w") as f:
        f.write(content)
    return filepath

@pytest.fixture(scope="module")
def test_files():
    # Cria arquivos de teste
    file1 = create_test_file("test1.txt", "Arquivo de teste 1")
    file2 = create_test_file("test2.txt", "Arquivo de teste 2")
    yield [file1, file2]
    # Remove arquivos após o teste
    for file in [file1, file2]:
        os.remove(file)

def test_root_endpoint():
    # Testa o endpoint raiz
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_process_multiple_files(test_files):
    # Simula envio de arquivos
    files = [
        ("files", open(test_files[0], "rb")),
        ("files", open(test_files[1], "rb")),
    ]
    response = client.post("/process-multiple-files", files=files)

    assert response.status_code == 200
    data = response.json()

    # Validações de resultado
    assert "results" in data
    assert len(data["results"]) == len(test_files)

    for result in data["results"]:
        assert "filename" in result
        assert "prediction" in result
        assert "heatmap" in result
        assert result["prediction"] in ["Positive", "Negative"]
        assert isinstance(result["heatmap"], str)  # Base64 é uma string

def test_invalid_file_format():
    # Testa envio de arquivo inválido
    invalid_file = create_test_file("invalid_file.jpg", "Conteúdo inválido")
    files = [("files", open(invalid_file, "rb"))]
    response = client.post("/process-multiple-files", files=files)

    assert response.status_code == 500
    os.remove(invalid_file)

def test_empty_request():
    # Testa envio sem arquivos
    response = client.post("/process-multiple-files")
    assert response.status_code == 422  # Código de erro para entrada inválida
