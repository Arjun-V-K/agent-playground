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
      cwd: '/home/pi/wwebjs-bot/agent-api',
      env: { ENV: 'production' },
    },
    {
      name: 'fastapi-leetcode',
      script: 'uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8001 --reload',
      interpreter: 'python3',
      cwd: '/home/pi/wwebjs-bot/leetcode-api',
      env: { ENV: 'production' },
    },
  ],
};