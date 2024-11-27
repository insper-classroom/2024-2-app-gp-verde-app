import React, { useState } from "react";
import { Box, Button, Typography, TextField, CircularProgress, IconButton } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";

function App() {
  const [file, setFile] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [heatmap, setHeatmap] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleClearFile = () => {
    setFile(null);
    setPrediction(null);
    setHeatmap(null);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!file) {
      setError("Por favor, selecione um arquivo .txt");
      return;
    }

    setError(null);
    setPrediction(null);
    setHeatmap(null);
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      // Fazer a requisição para /predict
      const predictResponse = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData,
      });

      if (!predictResponse.ok) {
        const errorData = await predictResponse.json();
        throw new Error(errorData.detail || "Erro na requisição de predição.");
      }

      const predictData = await predictResponse.json();
      setPrediction(predictData.prediction);

      // Fazer a requisição para /generate-heatmap
      const heatmapResponse = await fetch("http://127.0.0.1:8000/generate-heatmap", {
        method: "POST",
        body: formData,
      });

      if (!heatmapResponse.ok) {
        const errorData = await heatmapResponse.json();
        throw new Error(errorData.detail || "Erro na geração do heatmap.");
      }

      const blob = await heatmapResponse.blob();
      const heatmapUrl = URL.createObjectURL(blob);
      setHeatmap(heatmapUrl);
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
        Modelo de Predição e Heatmap
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
          Selecionar Arquivo
          <input
            type="file"
            hidden
            accept=".txt"
            onChange={handleFileChange}
          />
        </Button>
        {file && (
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
              {file.name}
            </Typography>
            <IconButton color="error" onClick={handleClearFile}>
              <DeleteIcon />
            </IconButton>
          </Box>
        )}
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading || !file}
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
        {prediction && (
          <Box sx={{ marginTop: 3, width: "100%", textAlign: "center" }}>
            <Typography variant="h6">Resultado da Predição:</Typography>
            <Typography
              variant="body1"
              sx={{
                backgroundColor: "#f4f4f4",
                padding: 2,
                borderRadius: 1,
                marginTop: 1,
              }}
            >
              {JSON.stringify(prediction, null, 2)}
            </Typography>
          </Box>
        )}
        {heatmap && (
          <Box sx={{ marginTop: 3, width: "100%", textAlign: "center" }}>
            <Typography variant="h6">Heatmap Gerado:</Typography>
            <img
              src={heatmap}
              alt="Heatmap"
              style={{
                maxWidth: "100%",
                height: "auto",
                border: "1px solid #ddd",
                borderRadius: "5px",
              }}
            />
          </Box>
        )}
      </Box>
    </Box>
  );
}

export default App;
