import React, { useState } from "react";
import {
  Box,
  Button,
  Typography,
  CircularProgress,
  IconButton,
  Container,
  Card,
  CardContent,
  Grid,
  Modal,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { motion } from "framer-motion";

const theme = createTheme({
  typography: {
    fontFamily: "Poppins, sans-serif",
  },
  palette: {
    primary: {
      main: "#ff6800",
    },
    secondary: {
      main: "#00004b",
    },
  },
});

const containerVariants = {
  hidden: { opacity: 0, y: 75 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 1.5, type: "spring" },
  },
};

const buttonVariants = {
  hidden: { opacity: 0, x: 200 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 1.5, type: "spring" },
  },
};

const titleVariants = {
  hidden: { opacity: 0, y: -100 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 1, type: "spring" },
  },
};

function App() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Novo estado para o modal
  const [openModal, setOpenModal] = useState(false);
  const [modalImage, setModalImage] = useState(null);

  const handleFileChange = (event) => {
    setFiles(Array.from(event.target.files));
  };

  const handleClearFiles = () => {
    setFiles([]);
    setResults([]);
    setError(null);
  };

  const handleRemoveFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
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
      const response = await fetch(
        "http://0.0.0.0:8000/process-multiple-files",
        {
          method: "POST",
          body: formData,
        }
      );

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

  // Funções para o modal
  const handleOpenModal = (image) => {
    setModalImage(image);
    setOpenModal(true);
  };

  const handleCloseModal = () => {
    setOpenModal(false);
    setModalImage(null);
  };

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          minHeight: "100vh",
          backgroundColor: "#f9f9f9",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Container maxWidth="md" sx={{ flexGrow: 1 }}>
          <motion.div
            initial="hidden"
            animate="visible"
            variants={titleVariants}
            style={{ marginTop: "50px", textAlign: "center" }}
          >
            <Typography variant="h3" color="secondary">
              Modelo Sprint Session 4
            </Typography>
            <Typography variant="h6" color="textSecondary" sx={{ mt: 2 }}>
              Carregue seus arquivos .txt para gerar predições e heatmaps
            </Typography>
          </motion.div>

          <motion.div
            initial="hidden"
            animate="visible"
            variants={containerVariants}
            style={{ marginTop: "50px" }}
          >
            <Card
              sx={{
                padding: 4,
                boxShadow: 3,
                borderRadius: 2,
                backgroundColor: "#ffffff",
              }}
            >
              <CardContent>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} sm={8}>
                    <Button
                      variant="contained"
                      component="label"
                      fullWidth
                      color="secondary"
                      sx={{
                        height: "56px",
                        fontSize: "16px",
                        textTransform: "none",
                        "&:hover": {
                          backgroundColor: "#333333",
                          color: "#ffffff",
                        },
                      }}
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
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Button
                      variant="contained"
                      onClick={handleSubmit}
                      disabled={loading || files.length === 0}
                      fullWidth
                      color="primary"
                      sx={{
                        height: "56px",
                        fontSize: "16px",
                        textTransform: "none",
                        color: files.length > 0 ? "#ffffff" : "inherit",
                      }}
                    >
                      {loading ? (
                        <CircularProgress size={24} color="inherit" />
                      ) : (
                        "Enviar"
                      )}
                    </Button>
                  </Grid>
                </Grid>

                {files.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Box
                      sx={{
                        maxHeight: 200,
                        overflowY: "auto",
                        border: "1px solid #e0e0e0",
                        borderRadius: 1,
                      }}
                    >
                      {files.map((file, index) => (
                        <Box
                          key={index}
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            p: 1,
                            borderBottom:
                              index !== files.length - 1
                                ? "1px solid #e0e0e0"
                                : "none",
                          }}
                        >
                          <Typography variant="body1">{file.name}</Typography>
                          <IconButton
                            color="error"
                            onClick={() => handleRemoveFile(index)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      ))}
                    </Box>
                    <Button
                      variant="outlined"
                      color="error"
                      onClick={handleClearFiles}
                      sx={{ mt: 1 }}
                    >
                      Remover Todos
                    </Button>
                  </Box>
                )}

                {error && (
                  <Typography
                    color="error"
                    variant="body2"
                    sx={{ marginTop: 2 }}
                  >
                    {error}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {results.length > 0 && (
            <motion.div
              initial="hidden"
              animate="visible"
              variants={containerVariants}
              style={{ marginTop: "50px" }}
            >
              <Typography
                variant="h4"
                color="secondary"
                sx={{ textAlign: "center", mb: 5 }}
              >
                Resultados
              </Typography>
              <Grid container spacing={4}>
                {results.map((result, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card
                      sx={{
                        height: "100%",
                        display: "flex",
                        flexDirection: "column",
                        boxShadow: 3,
                        borderRadius: 2,
                      }}
                    >
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" gutterBottom>
                          {result.filename}
                        </Typography>
                        <Typography variant="body1" sx={{ mb: 2 }}>
                          Predição: {result.prediction}
                        </Typography>
                        <Box
                          sx={{
                            cursor: "pointer",
                            "&:hover": {
                              opacity: 0.8,
                            },
                          }}
                          onClick={() => handleOpenModal(result.heatmap)}
                        >
                          <img
                            src={`data:image/png;base64,${result.heatmap}`}
                            alt={`Heatmap ${result.filename}`}
                            style={{
                              width: "100%",
                              height: "auto",
                              borderRadius: "5px",
                            }}
                          />
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </motion.div>
          )}
        </Container>

        {/* Modal para exibir a imagem ampliada */}
        <Modal
          open={openModal}
          onClose={handleCloseModal}
          sx={{ display: "flex", alignItems: "center", justifyContent: "center" }}
        >
          <Box
            sx={{
              maxWidth: "100%",
              maxHeight: "100%",
              outline: "none",
            }}
            onClick={handleCloseModal}
          >
            {modalImage && (
              <img
                src={`data:image/png;base64,${modalImage}`}
                alt="Heatmap Ampliado"
                style={{
                  width: "60%",
                  height: "60%",
                  display: "block",
                  margin: "0 auto",
                  borderRadius: "5px",
                }}
              />
            )}
          </Box>
        </Modal>

        <Box
          sx={{
            backgroundColor: "#000000",
            color: "#ffffff",
            py: 2,
            textAlign: "center",
          }}
        >
          <Typography variant="body2">
            © {new Date().getFullYear()} Sprint Session - Grupo Verde
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;