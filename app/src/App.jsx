import React, { useState } from "react";
import { Box, Button, Typography, CircularProgress, IconButton } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";

function App() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setFiles(Array.from(event.target.files));
  };

  const handleClearFiles = () => {
    setFiles([]);
    setResults([]);
    setError(null);
  };

  const handleSubmit = async () => {
    if (files.length === 0) {
      setError("Por favor, selecione pelo menos um arquivo .txt");
      return;
    }

    setError(null);
    setResults([]);
    setLoading(true);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("http://127.0.0.1:8000/process-multiple-files", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Erro ao processar os arquivos.");
      }

      const data = await response.json();
      setResults(data.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        padding: 2,
        backgroundColor: "#f9f9f9",
      }}
    >
      <Typography variant="h4" sx={{ marginBottom: 3 }}>
        Modelo de Predição e Heatmap (Múltiplos Arquivos)
      </Typography>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          width: "100%",
          maxWidth: 400,
        }}
      >
        <Button
          variant="contained"
          component="label"
          fullWidth
          sx={{ marginBottom: 2 }}
        >
          Selecionar Arquivos
          <input
            type="file"
            hidden
            multiple
            accept=".txt"
            onChange={handleFileChange}
          />
        </Button>
        {files.length > 0 && (
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              width: "100%",
              marginBottom: 2,
              backgroundColor: "#fff",
              padding: 1,
              borderRadius: 1,
              boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
            }}
          >
            <Typography variant="body1" sx={{ overflow: "hidden", textOverflow: "ellipsis" }}>
              {files.length} arquivo(s) selecionado(s)
            </Typography>
            <IconButton color="error" onClick={handleClearFiles}>
              <DeleteIcon />
            </IconButton>
          </Box>
        )}
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading || files.length === 0}
          fullWidth
          sx={{ marginBottom: 2 }}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : "Enviar"}
        </Button>
        {error && (
          <Typography
            color="error"
            variant="body2"
            sx={{ marginTop: 1, textAlign: "center" }}
          >
            {error}
          </Typography>
        )}
        {results.length > 0 && (
          <Box sx={{ marginTop: 3, width: "100%" }}>
            {results.map((result, index) => (
              <Box key={index} sx={{ marginBottom: 3 }}>
                <Typography variant="h6">{`Arquivo: ${result.filename}`}</Typography>
                <Typography variant="body1" sx={{ marginBottom: 1 }}>
                  Predição: {result.prediction}
                </Typography>
                <img
                  src={`data:image/png;base64,${result.heatmap}`}
                  alt={`Heatmap ${result.filename}`}
                  style={{
                    maxWidth: "100%",
                    height: "auto",
                    border: "1px solid #ddd",
                    borderRadius: "5px",
                  }}
                />
              </Box>
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );
}

export default App;
