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
const path = require('path');

// Create Express app
const app = express();
app.use(bodyParser.json());

// Determine data path (use /app/data in production for Fly.io volume)
const dataPath = process.env.NODE_ENV === 'production' 
    ? '/app/data/.wwebjs_auth'
    : undefined;  // Use default local path in development

// Determine Chromium path
const chromiumPath = process.env.PUPPETEER_EXECUTABLE_PATH || undefined;

// Create WhatsApp client with optimized Puppeteer settings for containers
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: "rose-bot",
        dataPath: dataPath
    }),
    puppeteer: {
        headless: true,
        executablePath: chromiumPath,
        timeout: 180000,  // 3 minutes timeout
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-first-run',
            '--disable-accelerated-2d-canvas',
            '--no-zygote'
        ]
    }
});

// Store for Python callback
let pythonCallbackUrl = null;
let isReady = false;
let currentQR = null;  // Store current QR code for HTTP access

// QR Code event
client.on('qr', (qr) => {
    console.log('QR Code received. Scan with WhatsApp:');
    qrcode.generate(qr, { small: true });
    currentQR = qr;  // Store for HTTP access
    
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
    console.log('Has quoted message:', msg.hasQuotedMsg);
    
    // Forward to Python
    if (pythonCallbackUrl) {
        try {
            const fetch = require('node-fetch');
            
            // Get quoted message info if this is a reply
            let quotedParticipant = null;
            let quotedMsg = null;
            if (msg.hasQuotedMsg) {
                try {
                    const quoted = await msg.getQuotedMessage();
                    quotedParticipant = quoted.author || quoted.from;
                    quotedMsg = {
                        id: quoted.id._serialized,
                        body: quoted.body,
                        from: quoted.author || quoted.from
                    };
                    console.log('Quoted participant:', quotedParticipant);
                } catch (e) {
                    console.error('Error getting quoted message:', e);
                }
            }
            
            // Determine chat ID (for groups, use the group ID)
            const chatId = msg.from.includes('@g.us') ? msg.from : msg.from;
            const senderId = msg.author || msg.from;  // In groups, author is the sender
            
            console.log('Sending to Python - chatId:', chatId, 'senderId:', senderId);
            console.log('Python callback URL:', pythonCallbackUrl);
            
            const response = await fetch(pythonCallbackUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'message',
                    data: {
                        id: msg.id._serialized,
                        body: msg.body,
                        from: senderId,
                        chatId: chatId,
                        to: msg.to,
                        timestamp: msg.timestamp,
                        hasMedia: msg.hasMedia,
                        isGroup: msg.from.includes('@g.us'),
                        hasQuotedMsg: msg.hasQuotedMsg,
                        quotedMsg: quotedMsg,
                        quotedParticipant: quotedParticipant
                    }
                })
            });
            console.log('Python response status:', response.status);
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

// Group participant joined/added event
client.on('group_join', async (notification) => {
    console.log('Group join notification:', notification);
    
    // Forward to Python
    if (pythonCallbackUrl) {
        try {
            const fetch = require('node-fetch');
            
            // Get the participant IDs who joined
            const participantIds = notification.recipientIds || [];
            
            await fetch(pythonCallbackUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'group_join',
                    chatId: notification.chatId,
                    participants: participantIds,
                    author: notification.author  // Who added them (if added by admin)
                })
            });
        } catch (error) {
            console.error('Error forwarding group_join to Python:', error);
        }
    }
});

// Group participant left/removed event
client.on('group_leave', async (notification) => {
    console.log('Group leave notification:', notification);
    
    // Forward to Python
    if (pythonCallbackUrl) {
        try {
            const fetch = require('node-fetch');
            
            const participantIds = notification.recipientIds || [];
            
            await fetch(pythonCallbackUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'group_leave',
                    chatId: notification.chatId,
                    participants: participantIds,
                    author: notification.author
                })
            });
        } catch (error) {
            console.error('Error forwarding group_leave to Python:', error);
        }
    }
});

// Initialize client
client.initialize();

// ===== HTTP API for Python =====

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        ready: isReady,
        hasQR: currentQR !== null
    });
});

// Get QR code for authentication
app.get('/qr', (req, res) => {
    if (isReady) {
        return res.json({ authenticated: true, message: 'Already authenticated' });
    }
    if (!currentQR) {
        return res.status(202).json({ waiting: true, message: 'Waiting for QR code...' });
    }
    res.json({ qr: currentQR });
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

// Delete message
app.post('/delete-message', async (req, res) => {
    try {
        const { chatId, messageId } = req.body;
        
        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }
        
        const chat = await client.getChatById(chatId);
        const messages = await chat.fetchMessages({ limit: 50 });
        
        // Find the message by ID
        const msg = messages.find(m => m.id._serialized === messageId);
        
        if (msg) {
            await msg.delete(true);  // true = delete for everyone
            res.json({ success: true });
        } else {
            res.status(404).json({ error: 'Message not found' });
        }
    } catch (error) {
        console.error('Error deleting message:', error);
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

// Add participants to group
app.post('/group/:groupId/add', async (req, res) => {
    try {
        const { groupId } = req.params;
        const { participants } = req.body;  // Array of participant IDs
        
        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }
        
        const chat = await client.getChatById(groupId);
        
        // Ensure participants is an array
        const participantList = Array.isArray(participants) ? participants : [participants];
        
        // Validate that participants have valid WhatsApp IDs
        const validParticipants = [];
        for (const p of participantList) {
            try {
                // Check if the number is registered on WhatsApp
                const numberId = await client.getNumberId(p.replace('@c.us', ''));
                if (numberId) {
                    validParticipants.push(numberId._serialized);
                } else {
                    console.log(`Number ${p} is not registered on WhatsApp`);
                }
            } catch (e) {
                console.log(`Error checking number ${p}:`, e.message);
                validParticipants.push(p);  // Try anyway
            }
        }
        
        if (validParticipants.length === 0) {
            return res.status(400).json({ error: 'No valid WhatsApp numbers found' });
        }
        
        const result = await chat.addParticipants(validParticipants);
        
        res.json({ success: true, result });
    } catch (error) {
        console.error('Error adding participants:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get group invite link
app.get('/group/:groupId/invite', async (req, res) => {
    try {
        const { groupId } = req.params;
        
        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }
        
        const chat = await client.getChatById(groupId);
        const inviteCode = await chat.getInviteCode();
        
        res.json({ 
            success: true, 
            inviteCode,
            inviteLink: `https://chat.whatsapp.com/${inviteCode}`
        });
    } catch (error) {
        console.error('Error getting invite link:', error);
        res.status(500).json({ error: error.message });
    }
});

// Health check endpoint for Fly.io
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok',
        whatsapp_ready: isReady,
        uptime: process.uptime()
    });
});

// Start server - bind to 0.0.0.0 for Fly.io
const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0';
app.listen(PORT, HOST, () => {
    console.log(`WhatsApp Bridge running on ${HOST}:${PORT}`);
    console.log('Waiting for WhatsApp authentication...');
});
