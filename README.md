# 2024-2-APP-GP-VERDE-APP

## Descrição do Projeto

Este é um projeto desenvolvido para a Sprint Session do 4º semestre de 2024/2 no Insper, em parceria com a DASA. O projeto consiste em um sistema completo com:

- **Frontend:** Implementado em React + Vite.
- **Backend:** Implementado em FastAPI.

**Link para acessar o site do projeto:** [http://3.81.205.150](http://3.81.205.150)

## Estrutura do Repositório

- **`app/`**: Contém o código do frontend (React + Vite).
- **`back/`**: Contém o código do backend (FastAPI).

---

## Instalação do AWS CLI e DVC

### **1. Instalar o Python**
Certifique-se de que o Python está instalado em sua máquina:

1. Verifique a versão do Python:
   ```bash
   python3 --version
   ```
2. Caso não esteja instalado, siga as instruções específicas do seu sistema operacional para instalá-lo.

### **2. Instalar o Node.js**
Certifique-se de que o Node.js está instalado em sua máquina:

1. Verifique a versão do Node.js:
   ```bash
   node --version
   ```
2. Caso não esteja instalado, baixe o instalador do [site oficial do Node.js](https://nodejs.org) e siga as instruções.

### **3. Instalar o AWS CLI**

#### **Windows**

1. Baixe o instalador oficial: [AWS CLI para Windows](https://awscli.amazonaws.com/AWSCLIV2.msi)
2. Execute o arquivo `.msi` e siga as instruções do instalador.
3. Verifique a instalação:
   ```bash
   aws --version
   ```

#### **macOS**

1. Baixe o pacote do instalador:
   ```bash
   curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
   ```
2. Instale com o comando:
   ```bash
   sudo installer -pkg AWSCLIV2.pkg -target /
   ```
3. Verifique a instalação:
   ```bash
   aws --version
   ```

#### **Linux**

1. Baixe o instalador:
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   ```
2. Extraia o arquivo:
   ```bash
   unzip awscliv2.zip
   ```
3. Execute o instalador:
   ```bash
   sudo ./aws/install
   ```
4. Verifique a instalação:
   ```bash
   aws --version
   ```

### **4. Instalar o DVC**

#### **Via pip (Recomendado)**

1. Certifique-se de que o Python está instalado:
   ```bash
   python3 --version
   ```
2. Instale o DVC:
   ```bash
   pip install dvc[s3]
   ```
3. Verifique a instalação:
   ```bash
   dvc --version
   ```

---

## Instalação e Execução do Projeto

### **1. Clonar o Repositório**

1. Clone o repositório para a sua máquina local:
   ```bash
   git clone https://github.com/insper-classroom/2024-2-app-gp-verde-app.git
   ```
2. Entre na pasta do projeto:
   ```bash
   cd 2024-2-app-gp-verde-app
   ```

### **2. Configuração Inicial do Repositório**

1. Configure suas credenciais AWS:
   ```bash
   aws configure
   ```
   Insira as seguintes informações:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (us-east-1)
   - Output format (deixe vazio ou "json")

2. Baixe os arquivos de dados gerenciados pelo DVC:
   ```bash
   dvc pull
   ```
3. Certifique-se de que todos os arquivos foram baixados corretamente antes de rodar o backend.

### **3. Configuração do Frontend**

1. Abra um terminal e entre na pasta do frontend:
   ```bash
   cd app
   ```
2. Instale as dependências:
   ```bash
   npm install
   ```
3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```
   O servidor será iniciado localmente em [http://localhost:5173](http://localhost:5173).

### **4. Configuração do Backend**

1. Abra outro terminal e entre na pasta do backend:
   ```bash
   cd back
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o servidor do FastAPI:
   ```bash
   uvicorn main:app --reload
   ```
   O servidor será iniciado localmente em [http://127.0.0.1:8000](http://127.0.0.1:8000).

> **Nota:** É necessário utilizar dois terminais separados para rodar o frontend e o backend simultaneamente.

---

## Contribuições

Este repositório foi desenvolvido por:

- Giovanny Russo
- Leonardo Freitas
- Luigi Orlandi
- Thiago Penha

