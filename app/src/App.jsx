import React, { useState } from 'react';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePredict = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/predict/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ feature: parseFloat(input) }),
      });
      const data = await response.json();
      setPrediction(data.prediction);
    } catch (error) {
      console.error('Erro ao fazer a predição:', error);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <h1>Modelo de Machine Learning</h1>
      <input
        type="number"
        placeholder="Digite um número"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button onClick={handlePredict} disabled={loading || !input}>
        {loading ? 'Carregando...' : 'Fazer Predição'}
      </button>
      {prediction !== null && (
        <p>Predição do modelo: <strong>{prediction}</strong></p>
      )}
    </div>
  );
}

export default App;
