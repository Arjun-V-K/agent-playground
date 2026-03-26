module.exports = {
  apps: [
    {
      name: 'whatsapp-bot',
      script: 'index.js',
      cwd: '/home/pi/wwebjs-bot',
      env: { NODE_ENV: 'production' },
    },
    {
      name: 'fastapi-agent',
      script: 'uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000 --reload',
      interpreter: 'python3',
      cwd: '/home/pi/wwebjs-bot/agent',
      env: { ENV: 'production' },
    },
  ],
};