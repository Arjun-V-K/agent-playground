const { Client, LocalAuth } = require('whatsapp-web.js');
const { askLLM } = require('./ollamaService');
const qrcode = require('qrcode-terminal');


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

// Listen for QR code
client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
    console.log("Scan the QR code above with WhatsApp on your phone");
});

// Bot ready
client.on('ready', () => {
    console.log('Hello World bot is ready!');
});

// Simple message handler
client.on('message', async msg => {
    
    // Ignore own messages
    if (msg.fromMe) return;

    const botNumber = client.info.wid._serialized;
    // const contact = await client.getContactById(msg.mentionedIds[0]);
    var isMentioned = false;
    // console.log(botNumber)
    // console.log(msg.mentionedIds)
    // console.log(contact.id._serialized)

    for (const id of msg.mentionedIds) {
        try {
            const contact = await client.getContactById(id);
            if (contact.id._serialized === botNumber) {
                isMentioned = true;
                break;
            }
        } catch (error) {
            console.error('Error checking mention:', error);
        }
    }

    // Only respond when bot is mentioned in group
    if (isMentioned) {
        const userPrompt = msg.body.replace(/@\S+\s?/g, '').trim();

        console.log('User:', userPrompt);

        const reply = await askLLM(userPrompt);

        // WhatsApp message length limit safety
        const safeReply = reply.substring(0, 1500);

        msg.reply(safeReply);
    }
});

client.initialize();
