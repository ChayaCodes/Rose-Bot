/**
 * WhatsApp Web Bridge for Python Bot
 * 
 * This Node.js server acts as a bridge between Python and WhatsApp Web.
 * It handles the WhatsApp Web connection and provides HTTP API for Python to interact with.
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const bodyParser = require('body-parser');

// Create Express app
const app = express();
app.use(bodyParser.json());

// Create WhatsApp client
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: "rose-bot"
    }),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox']
    }
});

// Store for Python callback
let pythonCallbackUrl = null;
let isReady = false;

// QR Code event
client.on('qr', (qr) => {
    console.log('QR Code received. Scan with WhatsApp:');
    qrcode.generate(qr, { small: true });
    
    // You can also send QR to Python if needed
    if (pythonCallbackUrl) {
        // Send QR to Python
    }
});

// Ready event
client.on('ready', () => {
    console.log('WhatsApp Client is ready!');
    isReady = true;
});

// Message received event
client.on('message', async (msg) => {
    console.log('Message received:', msg.body);
    
    // Forward to Python
    if (pythonCallbackUrl) {
        try {
            const fetch = require('node-fetch');
            await fetch(pythonCallbackUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'message',
                    data: {
                        id: msg.id._serialized,
                        body: msg.body,
                        from: msg.from,
                        to: msg.to,
                        timestamp: msg.timestamp,
                        hasMedia: msg.hasMedia,
                        isGroup: msg.from.includes('@g.us')
                    }
                })
            });
        } catch (error) {
            console.error('Error forwarding message to Python:', error);
        }
    }
});

// Disconnected event
client.on('disconnected', (reason) => {
    console.log('Client was logged out:', reason);
    isReady = false;
});

// Initialize client
client.initialize();

// ===== HTTP API for Python =====

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        ready: isReady
    });
});

// Set Python callback URL
app.post('/set-callback', (req, res) => {
    pythonCallbackUrl = req.body.url;
    res.json({ success: true });
});

// Send message
app.post('/send-message', async (req, res) => {
    try {
        const { chatId, message } = req.body;
        
        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }
        
        // Send message without trying to mark as read
        const sentMsg = await client.sendMessage(chatId, message, { sendSeen: false });
        
        res.json({
            success: true,
            messageId: sentMsg.id._serialized
        });
    } catch (error) {
        console.error('Error sending message:', error);
        res.status(500).json({ error: error.message });
    }
});

// Send media
app.post('/send-media', async (req, res) => {
    try {
        const { chatId, mediaUrl, caption } = req.body;
        
        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }
        
        const MessageMedia = require('whatsapp-web.js').MessageMedia;
        const media = await MessageMedia.fromUrl(mediaUrl);
        
        const sentMsg = await client.sendMessage(chatId, media, { caption });
        
        res.json({
            success: true,
            messageId: sentMsg.id._serialized
        });
    } catch (error) {
        console.error('Error sending media:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get chat info
app.get('/chat/:chatId', async (req, res) => {
    try {
        const { chatId } = req.params;
        
        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }
        
        const chat = await client.getChatById(chatId);
        
        res.json({
            id: chat.id._serialized,
            name: chat.name,
            isGroup: chat.isGroup,
            participants: chat.isGroup ? chat.participants.length : null
        });
    } catch (error) {
        console.error('Error getting chat:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get group members
app.get('/group/:groupId/members', async (req, res) => {
    try {
        const { groupId } = req.params;
        
        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }
        
        const chat = await client.getChatById(groupId);
        
        if (!chat.isGroup) {
            return res.status(400).json({ error: 'Not a group' });
        }
        
        const participants = chat.participants.map(p => ({
            id: p.id._serialized,
            isAdmin: p.isAdmin,
            isSuperAdmin: p.isSuperAdmin
        }));
        
        res.json({ participants });
    } catch (error) {
        console.error('Error getting group members:', error);
        res.status(500).json({ error: error.message });
    }
});

// Remove participant from group
app.post('/group/:groupId/remove', async (req, res) => {
    try {
        const { groupId } = req.params;
        const { participantId } = req.body;
        
        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }
        
        const chat = await client.getChatById(groupId);
        await chat.removeParticipants([participantId]);
        
        res.json({ success: true });
    } catch (error) {
        console.error('Error removing participant:', error);
        res.status(500).json({ error: error.message });
    }
});

// Promote participant to admin
app.post('/group/:groupId/promote', async (req, res) => {
    try {
        const { groupId } = req.params;
        const { participantId } = req.body;
        
        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }
        
        const chat = await client.getChatById(groupId);
        await chat.promoteParticipants([participantId]);
        
        res.json({ success: true });
    } catch (error) {
        console.error('Error promoting participant:', error);
        res.status(500).json({ error: error.message });
    }
});

// Demote participant from admin
app.post('/group/:groupId/demote', async (req, res) => {
    try {
        const { groupId } = req.params;
        const { participantId } = req.body;
        
        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }
        
        const chat = await client.getChatById(groupId);
        await chat.demoteParticipants([participantId]);
        
        res.json({ success: true });
    } catch (error) {
        console.error('Error demoting participant:', error);
        res.status(500).json({ error: error.message });
    }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`WhatsApp Bridge running on port ${PORT}`);
    console.log('Waiting for WhatsApp authentication...');
});
