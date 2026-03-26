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
    console.error('Ollama error:', err);
    return "Someone tell Arjun there's a problem with my AI.";
  }
}

const AGENT_URL = 'http://localhost:8000/invoke';

async function askLLMv2(userMessage) {
  try {
    const request = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ msg: userMessage })
    };

    console.log('[OllamaService] askLLMv2 Request:', request);

    const response = await fetch(AGENT_URL, request);
    if (!response.ok) {
      throw new Error(`Agent HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log('[OllamaService] askLLMv2 Response:', data);

    if (!data || typeof data.msg !== 'string') {
      throw new Error('Invalid response format from agent');
    }

    let reply = data.msg.trim();
    reply = reply.replace(/^Assistant:\s*/i, '');
    return reply;
  } catch (err) {
    console.error('askLLMv2 error:', err);
    return "Someone tell Arjun there's a problem with my AI.";
  }
}

module.exports = { askLLM, askLLMv2 };
