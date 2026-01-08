import React, { useState } from 'react';
import './App.css';

function App() {
  const [pergunta, setPergunta] = useState('');
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setAnswer(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pergunta }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Backend envia erros no campo `detail`
        setError(data.detail || 'Ocorreu um erro ao processar a sua pergunta.');
      } else {
        setAnswer(data.answer ?? 'Sem resposta.');
      }
    } catch (err) {
      console.error(err);
      setError('Não foi possível conectar ao servidor. Verifique se o backend está em execução.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>FruitChatbot</h1>
        <p>Faça perguntas sobre preço ou estoque de frutas.</p>
        <form onSubmit={handleSubmit} className="chat-form">
          <input
            type="text"
            value={pergunta}
            onChange={(e) => setPergunta(e.target.value)}
            placeholder="Ex.: Quanto custa a banana?"
            className="chat-input"
          />
          <button type="submit" disabled={loading || !pergunta.trim()}>
            {loading ? 'Enviando...' : 'Enviar'}
          </button>
        </form>
        <div className="chat-response">
          {error && <p className="error">{error}</p>}
          {answer && !error && <p className="answer">{answer}</p>}
        </div>
      </header>
    </div>
  );
}

export default App;
