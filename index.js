const { Client, LocalAuth } = require('whatsapp-web.js');
const { askLLM, askLLMv2 } = require('./ollamaService');
const qrcode = require('qrcode-terminal');

console.log("Starting Bot...")

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        executablePath: '/usr/lib/chromium/chromium',
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    }
});


client.on('authenticated', () => {
    console.log('Authenticated with WhatsApp session.');
});

client.on('auth_failure', msg => {
    console.error('Auth failure:', msg);
});

client.on('change_state', state => {
    console.log('State changed:', state);
});

client.on('disconnected', reason => {
    console.warn('Client disconnected:', reason);
});

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
    console.log('Scan the QR code above with WhatsApp on your phone');
});

// Bot ready
client.on('ready', () => {
    console.log('Whatsapp Bot is ready!');
});

// Simple message handler
client.on('message', async msg => {
    const senderName = (await msg.getContact()).pushname
    console.log('Received message:', {
        from: msg.from,
        body: msg.body,
        mentionedIds: msg.mentionedIds,
        fromMe: msg.fromMe,
        fromName: senderName
    });


    // Ignore own messages
    if (msg.fromMe) return;
    if (!msg.body || msg.body.replace(/@\S+\s?/g, '').trim() === '') {
        console.log('Skipping empty message');
        return;
    }

    const botId = client.info?.wid?._serialized;

    let isMentioned = false;

    const mentions = await msg.getMentions();
    for (const contact of mentions) {
        if (contact.id._serialized === botId) {
            isMentioned = true;
        }
    }
    
    // Only respond when bot is mentioned in group
    if (isMentioned) {
        const userPrompt = msg.body.replace(/@\S+\s?/g, '').trim();

        console.log('User prompt:', userPrompt);

        // To show typing indicator
        const chat = await msg.getChat();
        chat.sendStateTyping();

        const reply = await askLLMv2(senderName, userPrompt);

        // WhatsApp message length limit safety
        const safeReply = reply.substring(0, 2000);

        console.log('Replying with:', safeReply);
        msg.reply(safeReply);
    } else {
        console.log('Bot not mentioned; ignoring message');
    }
});

client.initialize();
