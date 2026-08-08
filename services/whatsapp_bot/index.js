const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const FormData = require('form-data');

const API_URL = process.env.API_URL || 'http://backend:8000/api/whatsapp/webhook';

console.log('Starting WhatsApp Client...');

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: '/app/session' }),
    puppeteer: {
        executablePath: '/usr/bin/chromium-browser',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu'
        ]
    }
});

client.on('qr', (qr) => {
    console.log('\n======================================================');
    console.log('SCAN THIS QR CODE WITH YOUR WHATSAPP MOBILE APP:');
    console.log('======================================================\n');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ WhatsApp Web Client is connected and active!');
});

client.on('message', async (msg) => {
    try {
        const formData = new FormData();
        formData.append('From', msg.from);

        // Handle Voice Notes (audio / ptt)
        if (msg.hasMedia && (msg.type === 'audio' || msg.type === 'ptt' || msg.type === 'voice')) {
            console.log(`🎙️ Voice note detected from ${msg.from}. Downloading...`);
            
            const media = await msg.downloadMedia();
            if (!media || !media.data) {
                console.error('❌ Failed to download media payload from WhatsApp.');
                return msg.reply('⚠️ Could not download audio. Please record again.');
            }

            const audioBuffer = Buffer.from(media.data, 'base64');
            
            // CRITICAL FIX: Clean MIME type by removing '; codecs=opus'
            const rawMime = media.mimetype || 'audio/ogg';
            const cleanMime = rawMime.split(';')[0].trim(); // e.g. 'audio/ogg'

            formData.append('file', audioBuffer, {
                filename: 'voice_note.ogg',
                contentType: cleanMime
            });

            console.log(`📤 Forwarding audio buffer (${audioBuffer.length} bytes, ${cleanMime}) to FastAPI...`);

        } else if (msg.body) {
            console.log(`💬 Received text message from ${msg.from}: ${msg.body}`);
            formData.append('Body', msg.body);
        } else {
            return;
        }

        // Send to FastAPI
        const response = await axios.post(API_URL, formData, {
            headers: formData.getHeaders(),
            maxContentLength: Infinity,
            maxBodyLength: Infinity
        });

        if (response.data && response.data.reply) {
            await msg.reply(response.data.reply);
        }
    } catch (err) {
        // Detailed error log
        const errorDetails = err.response ? err.response.data : err.message;
        console.error('❌ Error handling message:', JSON.stringify(errorDetails));
        await msg.reply('⚠️ Sorry, there was an error processing your medical triage note.');
    }
});

client.initialize();