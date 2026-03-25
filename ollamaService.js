// ollamaService.js

const OLLAMA_URL = 'http://localhost:11434/api/generate';
const MODEL = 'phi3:3.8b';

async function askLLM(userMessage) {
  try {

    request = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: MODEL,
        prompt: `${userMessage}`,
        stream: false
      })
    }

    console.log('[OllamaService] Request: ', request);

    const response = await fetch(OLLAMA_URL, request);

    if (!response.ok) {
      throw new Error(`Ollama HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log('[OllamaService] Response: ', data);
    reply = data.response.trim();
    reply = reply.replace(/^Assistant:\s*/i, '');
    return reply;

  } catch (err) {
    console.error('Ollama error:', err.message);
    return 'LLM error.';
  }
}

module.exports = { askLLM };
