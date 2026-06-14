# wwebjs-bot

A WhatsApp bot built with `whatsapp-web.js` and a local Ollama-backed AI agent served via FastAPI.

## Overview

This repository contains:

- `index.js`: A WhatsApp bot that listens for mentions and forwards user prompts to a local AI service.
- `ollamaService.js`: A service module that calls a local FastAPI agent or Ollama API.
- `agent/main.py`: A FastAPI application exposing the `/invoke` endpoint.
- `agent/agent.py`: The agent logic using LangChain, LangGraph, and `langchain-ollama`.
- `app.config.js`: PM2 configuration for running both the Node bot and the Python FastAPI agent.

## Features

- Generates a WhatsApp QR code in the terminal for authentication.
- Responds only when the bot is mentioned in group chats.
- Uses a local Ollama model (`phi3:3.8b`) via a Python agent.
- Truncates responses to 1500 characters to stay within WhatsApp limits.

## Requirements

- Node.js
- Python 3
- `npm` and `pip`
- Local Ollama server running on `http://localhost:11434`
- Optional: `pm2` for `app.config.js` process management

## Setup

1. Install Node dependencies:

```bash
npm install
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Start the Ollama server and ensure the model `phi3:3.8b` is available.

4. Start the Python agent service:

```bash
cd agent
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

5. Run the WhatsApp bot:

```bash
cd ..
node index.js
```

## Using PM2

If you prefer process management with PM2, use the included `app.config.js`:

```bash
npm install -g pm2
npm install
pip install -r requirements.txt
pm2 start app.config.js
```

## How it works

- `index.js` creates a `whatsapp-web.js` client using `LocalAuth` and Chromium.
- When a QR code is generated, it is printed in the terminal via `qrcode-terminal`.
- The bot listens for messages and checks whether it is mentioned in a group chat.
- If mentioned, the message text is forwarded to `askLLMv2` in `ollamaService.js`.
- `askLLMv2` sends the prompt to the local FastAPI agent at `http://localhost:8000/invoke`.
- The agent uses `langchain-ollama` and a system prompt in `agent/agent.py`.

## Agent behavior

The agent is configured with a simple system prompt:

> "You are Groot. You will reply with 'I am groot' to all questions."

This means the bot is expected to respond as Groot to incoming prompts.

## Files

- `index.js`: WhatsApp bot entry point.
- `ollamaService.js`: Local AI request handling for both Ollama and FastAPI agent.
- `app.config.js`: PM2 app definitions for Node and Python services.
- `agent/main.py`: FastAPI wrapper for the agent.
- `agent/agent.py`: Agent graph and model invocation logic.
- `requirements.txt`: Python dependencies.
- `package.json`: Node dependencies.

## Notes

- Update the Chromium executable path in `index.js` if your system uses a different location.
- The bot currently only answers when mentioned in groups.
- If the local agent or Ollama service fails, the bot returns a fallback error message.
