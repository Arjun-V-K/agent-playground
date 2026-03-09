// ollamaService.js

const OLLAMA_URL = 'http://localhost:11434/api/generate';
const MODEL = 'tinyllama';

async function askLLM(userMessage) {
  try {

    request = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: MODEL,
        prompt: `Answer in ONE SHORT sentence.
Maximum 10 words.
Only give the final answer.

Question: ${userMessage}
Answer: `,
        stream: false,
        options: {
          temperature: 0.3,
          num_predict: 60,
          repeat_penalty: 1.2,
          stop: ["Question:", "\n\n"]
        }
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
