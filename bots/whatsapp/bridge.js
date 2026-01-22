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
const fs = require('fs');

// Create Express app
const app = express();
app.use(bodyParser.json());

// Determine data path (use /app/data in production for Fly.io volume)
const dataPath = process.env.NODE_ENV === 'production' 
    ? '/app/data/.wwebjs_auth'
    : undefined;  // Use default local path in development

// Create WhatsApp client
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: "rose-bot",
        dataPath: dataPath
    }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    }
});

// Store for Python callback
let pythonCallbackUrl = null;
let isReady = false;

// Load bridge capabilities (future-proof API surface)
let bridgeCapabilities = { version: 'unknown', actions: [], events: [], allowedMethods: {} };
try {
    const capabilitiesPath = path.join(__dirname, 'bridge_capabilities.json');
    const raw = fs.readFileSync(capabilitiesPath, 'utf8');
    bridgeCapabilities = JSON.parse(raw);
} catch (e) {
    console.warn('bridge_capabilities.json not found or invalid. Using minimal capabilities.');
}

const ALLOW_UNSAFE_CALLS = process.env.BRIDGE_ALLOW_UNSAFE_CALLS === 'true';

async function forwardToPython(payload) {
    if (!pythonCallbackUrl) return;
    try {
        const fetch = require('node-fetch');
        await fetch(pythonCallbackUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (error) {
        console.error('Error forwarding event to Python:', error);
    }
}

// QR Code event
client.on('qr', (qr) => {
    console.log('QR Code received. Scan with WhatsApp:');
    qrcode.generate(qr, { small: true });
    
    forwardToPython({
        type: 'qr',
        data: { qr }
    });
});

// Ready event
client.on('ready', () => {
    console.log('WhatsApp Client is ready!');
    isReady = true;
    forwardToPython({ type: 'ready', data: { ready: true } });
});

// Message received event
client.on('message', async (msg) => {
    console.log('Message received:', msg.body);
    console.log('Has quoted message:', msg.hasQuotedMsg);
    
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
                from: quoted.author || quoted.from,
                timestamp: quoted.timestamp
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
    
    await forwardToPython({
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
            isPrivate: msg.from.includes('@s.whatsapp.net'),
            hasQuotedMsg: msg.hasQuotedMsg,
            quotedMsg: quotedMsg,
            quotedParticipant: quotedParticipant,
            type: msg.type,
            isForwarded: msg.isForwarded,
            hasReaction: msg.hasReaction,
            mentionedIds: msg.mentionedIds || []
        }
    });
});

// Disconnected event
client.on('disconnected', (reason) => {
    console.log('Client was logged out:', reason);
    isReady = false;
    forwardToPython({ type: 'disconnected', data: { reason } });
});

client.on('authenticated', () => {
    forwardToPython({ type: 'authenticated', data: { success: true } });
});

client.on('auth_failure', (message) => {
    forwardToPython({ type: 'auth_failure', data: { message } });
});

client.on('change_state', (state) => {
    forwardToPython({ type: 'change_state', data: { state } });
});

client.on('change_battery', (batteryInfo) => {
    forwardToPython({ type: 'change_battery', data: batteryInfo });
});

client.on('message_create', async (msg) => {
    await forwardToPython({
        type: 'message_create',
        data: { id: msg.id._serialized, body: msg.body, from: msg.from, timestamp: msg.timestamp }
    });
});

client.on('message_edit', async (msg) => {
    await forwardToPython({
        type: 'message_edit',
        data: { id: msg.id._serialized, body: msg.body, from: msg.from, timestamp: msg.timestamp }
    });
});

client.on('message_ack', (msg, ack) => {
    forwardToPython({
        type: 'message_ack',
        data: { id: msg?.id?._serialized, ack }
    });
});

client.on('message_reaction', (reaction) => {
    forwardToPython({
        type: 'message_reaction',
        data: {
            id: reaction?.id?._serialized,
            msgId: reaction?.msgId?._serialized,
            reaction: reaction?.reaction,
            senderId: reaction?.senderId?._serialized,
            timestamp: reaction?.timestamp
        }
    });
});

client.on('message_revoke_everyone', async (msg) => {
    await forwardToPython({
        type: 'message_revoke_everyone',
        data: { id: msg.id._serialized, from: msg.from, timestamp: msg.timestamp }
    });
});

client.on('message_revoke_me', async (msg) => {
    await forwardToPython({
        type: 'message_revoke_me',
        data: { id: msg.id._serialized, from: msg.from, timestamp: msg.timestamp }
    });
});

client.on('group_update', (notification) => {
    forwardToPython({
        type: 'group_update',
        data: {
            chatId: notification.chatId,
            author: notification.author,
            type: notification.type,
            timestamp: notification.timestamp
        }
    });
});

client.on('group_admin_changed', (notification) => {
    forwardToPython({
        type: 'group_admin_changed',
        data: {
            chatId: notification.chatId,
            author: notification.author,
            type: notification.type,
            recipientIds: notification.recipientIds || [],
            timestamp: notification.timestamp
        }
    });
});

client.on('group_membership_request', (notification) => {
    forwardToPython({
        type: 'group_membership_request',
        data: {
            chatId: notification.chatId,
            author: notification.author,
            recipientIds: notification.recipientIds || [],
            timestamp: notification.timestamp
        }
    });
});

client.on('incoming_call', (call) => {
    forwardToPython({
        type: 'incoming_call',
        data: {
            from: call.from,
            isGroup: call.isGroup,
            isVideo: call.isVideo,
            timestamp: call.timestamp
        }
    });
});

client.on('media_uploaded', (msg) => {
    forwardToPython({
        type: 'media_uploaded',
        data: { id: msg?.id?._serialized, from: msg?.from, timestamp: msg?.timestamp }
    });
});

client.on('vote_update', (vote) => {
    forwardToPython({
        type: 'vote_update',
        data: vote
    });
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
                    author: notification.author,  // Who added them (if added by admin)
                    isGroup: true,
                    timestamp: notification.timestamp
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
                    author: notification.author,
                    isGroup: true,
                    timestamp: notification.timestamp
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
        ready: isReady
    });
});

// Set Python callback URL
app.post('/set-callback', (req, res) => {
    pythonCallbackUrl = req.body.url;
    res.json({ success: true });
});

// Capabilities: full API surface (current + future)
app.get('/capabilities', (req, res) => {
    res.json({
        success: true,
        ready: isReady,
        allowUnsafeCalls: ALLOW_UNSAFE_CALLS,
        capabilities: bridgeCapabilities
    });
});

function isMethodAllowed(scope, method) {
    if (ALLOW_UNSAFE_CALLS) return true;
    const allowed = bridgeCapabilities.allowedMethods || {};
    const methods = allowed[scope] || [];
    return methods.includes(method);
}

function serializeResult(result) {
    if (result === undefined) return null;
    if (result === null) return null;
    if (typeof result === 'string' || typeof result === 'number' || typeof result === 'boolean') {
        return result;
    }
    if (Array.isArray(result)) {
        return result.map(serializeResult);
    }
    if (typeof result === 'object') {
        if (result.id && result.id._serialized) {
            return {
                id: result.id._serialized,
                body: result.body,
                from: result.from,
                to: result.to,
                timestamp: result.timestamp,
                type: result.type,
                name: result.name,
                isGroup: result.isGroup,
                isUser: result.isUser,
                isBusiness: result.isBusiness,
                isEnterprise: result.isEnterprise,
                isBlocked: result.isBlocked,
                number: result.number,
                pushname: result.pushname,
                shortName: result.shortName
            };
        }
        return result;
    }
    return result;
}

async function resolveTarget(scope, id) {
    if (scope === 'client') return client;
    if (!id) throw new Error('Missing id for scope: ' + scope);

    if (scope === 'chat' || scope === 'group' || scope === 'channel') {
        const chat = await client.getChatById(id);
        if (scope === 'group' && !chat.isGroup) {
            throw new Error('Target is not a group chat');
        }
        return chat;
    }

    if (scope === 'message') {
        const msg = await client.getMessageById(id);
        if (!msg) throw new Error('Message not found');
        return msg;
    }

    if (scope === 'contact') {
        const contact = await client.getContactById(id);
        if (!contact) throw new Error('Contact not found');
        return contact;
    }

    throw new Error('Unknown scope: ' + scope);
}

// Generic call endpoint for future expansion (covers most whatsapp-web.js methods)
app.post('/call', async (req, res) => {
    try {
        const { scope, method, id, args } = req.body;

        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }
        if (!scope || !method) {
            return res.status(400).json({ error: 'Missing scope or method' });
        }
        if (!isMethodAllowed(scope, method)) {
            return res.status(403).json({ error: 'Method not allowed' });
        }

        const target = await resolveTarget(scope, id);
        const fn = target[method];
        if (typeof fn !== 'function') {
            return res.status(400).json({ error: 'Method not found on target' });
        }

        const callArgs = Array.isArray(args) ? args : [];
        const result = await fn.apply(target, callArgs);

        res.json({
            success: true,
            result: serializeResult(result)
        });
    } catch (error) {
        console.error('Error in /call:', error);
        res.status(500).json({ error: error.message });
    }
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

// Send media from base64 (future-proof)
app.post('/send-media-base64', async (req, res) => {
    try {
        const { chatId, mimetype, data, filename, caption } = req.body;

        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }

        const { MessageMedia } = require('whatsapp-web.js');
        const media = new MessageMedia(mimetype, data, filename);
        const sentMsg = await client.sendMessage(chatId, media, { caption });

        res.json({ success: true, messageId: sentMsg.id._serialized });
    } catch (error) {
        console.error('Error sending media (base64):', error);
        res.status(500).json({ error: error.message });
    }
});

// Send message with mentions
app.post('/send-mention', async (req, res) => {
    try {
        const { chatId, message, mentionIds } = req.body;

        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }

        const mentions = [];
        if (Array.isArray(mentionIds)) {
            for (const id of mentionIds) {
                try {
                    const contact = await client.getContactById(id);
                    if (contact) mentions.push(contact);
                } catch (e) {
                    console.warn('Unable to resolve mention contact:', id);
                }
            }
        }

        const sentMsg = await client.sendMessage(chatId, message, { mentions });
        res.json({ success: true, messageId: sentMsg.id._serialized });
    } catch (error) {
        console.error('Error sending mention message:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get message by ID
app.get('/message/:messageId', async (req, res) => {
    try {
        const { messageId } = req.params;

        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }

        const msg = await client.getMessageById(messageId);
        if (!msg) {
            return res.status(404).json({ error: 'Message not found' });
        }

        res.json({ success: true, message: serializeResult(msg) });
    } catch (error) {
        console.error('Error getting message:', error);
        res.status(500).json({ error: error.message });
    }
});

// Download media from message
app.get('/message/:messageId/media', async (req, res) => {
    try {
        const { messageId } = req.params;

        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }

        const msg = await client.getMessageById(messageId);
        if (!msg) {
            return res.status(404).json({ error: 'Message not found' });
        }
        if (!msg.hasMedia) {
            return res.status(400).json({ error: 'Message has no media' });
        }

        const media = await msg.downloadMedia();
        res.json({
            success: true,
            media: {
                mimetype: media.mimetype,
                data: media.data,
                filename: media.filename,
                filesize: media.filesize
            }
        });
    } catch (error) {
        console.error('Error downloading media:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get contact by ID
app.get('/contact/:contactId', async (req, res) => {
    try {
        const { contactId } = req.params;

        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }

        const contact = await client.getContactById(contactId);
        if (!contact) {
            return res.status(404).json({ error: 'Contact not found' });
        }

        res.json({ success: true, contact: serializeResult(contact) });
    } catch (error) {
        console.error('Error getting contact:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get contact by phone number (various formats)
app.get('/contact/by-number/:number', async (req, res) => {
    try {
        const { number } = req.params;

        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }

        const numberId = await client.getNumberId(number.replace(/\D/g, ''));
        if (!numberId) {
            return res.status(404).json({ error: 'Number not registered' });
        }

        const contact = await client.getContactById(numberId._serialized);
        res.json({ success: true, contact: serializeResult(contact) });
    } catch (error) {
        console.error('Error getting contact by number:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get chat details (group/private detection)
app.get('/chat/:chatId/details', async (req, res) => {
    try {
        const { chatId } = req.params;

        if (!isReady) {
            return res.status(503).json({ error: 'Client not ready' });
        }

        const chat = await client.getChatById(chatId);
        res.json({
            success: true,
            chat: {
                id: chat.id._serialized,
                name: chat.name,
                isGroup: chat.isGroup,
                isReadOnly: chat.isReadOnly,
                isMuted: chat.isMuted,
                unreadCount: chat.unreadCount,
                timestamp: chat.timestamp,
                description: chat.description || null,
                participants: chat.isGroup ? chat.participants.length : null
            }
        });
    } catch (error) {
        console.error('Error getting chat details:', error);
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

        const participantIds = participants.map(p => p.id).filter(Boolean);
        try {
            if (participantIds.length > 0 && typeof client.getContactLidAndPhone === 'function') {
                const mappings = await client.getContactLidAndPhone(participantIds);
                if (Array.isArray(mappings) && mappings.length === participantIds.length) {
                    mappings.forEach((entry, idx) => {
                        participants[idx].lid = entry?.lid || null;
                        participants[idx].phone = entry?.pn || null;
                    });
                }
            }
        } catch (e) {
            console.warn('Failed to resolve LID/phone for participants:', e?.message || e);
        }
        
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
        
        // Check result codes
        const checkResult = (addResult) => {
            if (!addResult || typeof addResult !== 'object') {
                return { success: false, reason: 'No result' };
            }
            
            const results = [];
            for (const [participantId, entry] of Object.entries(addResult)) {
                const code = entry?.code ?? entry?.status;
                const message = entry?.message || '';
                const inviteSent = entry?.isInviteV4Sent === true;
                
                if (code === 200) {
                    results.push({ participantId, success: true, added: true, code });
                } else if (code === 403 && inviteSent) {
                    results.push({ participantId, success: true, added: false, inviteSent: true, message, code });
                } else if (code === 403) {
                    results.push({ participantId, success: false, added: false, message: 'Privacy settings prevent direct add, invite required', code });
                } else if (code === 409) {
                    results.push({ participantId, success: true, added: true, message: 'Already in group', code });
                } else {
                    results.push({ participantId, success: false, added: false, code, message });
                }
            }
            
            const anySuccess = results.some(r => r.success);
            const allAdded = results.every(r => r.added);
            return { success: anySuccess, allAdded, results };
        };

        let result;
        let lastError;
        
        const sendInviteLinkPrivately = async (participantIds) => {
            console.log('Getting invite code for group...');
            const inviteCode = await chat.getInviteCode();
            const inviteLink = `https://chat.whatsapp.com/${inviteCode}`;
            console.log('Invite link:', inviteLink);
            const sent = [];
            const failed = [];
            for (const participantId of participantIds) {
                try {
                    console.log(`Sending invite link to ${participantId}...`);
                    
                    // Extract phone number from participantId (remove @c.us)
                    const phoneNumber = participantId.replace('@c.us', '');
                    
                    // First check if the number is registered on WhatsApp
                    console.log(`Checking if ${phoneNumber} is registered on WhatsApp...`);
                    const numberId = await client.getNumberId(phoneNumber);
                    
                    if (!numberId) {
                        console.log(`${phoneNumber} is not registered on WhatsApp`);
                        failed.push(participantId);
                        continue;
                    }
                    
                    console.log(`Number ${phoneNumber} is registered, ID: ${numberId._serialized}`);
                    
                    // Use the correct ID format from getNumberId
                    const correctId = numberId._serialized;
                    const message = `הוזמנת להצטרף לקבוצה:\n${inviteLink}`;
                    
                    // Try using getContactLidAndPhone to get the LID, then getChatById with LID
                    try {
                        console.log('Trying getContactLidAndPhone method...');
                        const lidResults = await client.getContactLidAndPhone([correctId]);
                        console.log('getContactLidAndPhone result:', JSON.stringify(lidResults));
                        
                        if (lidResults && lidResults.length > 0) {
                            const lidResult = lidResults[0];
                            const chatId = lidResult.lid || lidResult.pn || correctId;
                            console.log(`Using chatId: ${chatId}`);
                            
                            const privateChat = await client.getChatById(chatId);
                            if (privateChat) {
                                await privateChat.sendMessage(message);
                                console.log(`Successfully sent invite link to ${participantId} via LID method`);
                                sent.push(participantId);
                                continue;
                            }
                        }
                        throw new Error('getContactLidAndPhone did not return usable results');
                    } catch (lidErr) {
                        console.log(`LID method failed: ${lidErr?.message}, trying direct sendMessage...`);
                        
                        // Fallback: try direct client.sendMessage
                        try {
                            await client.sendMessage(correctId, message);
                            console.log(`Successfully sent invite link to ${participantId} via direct sendMessage`);
                            sent.push(participantId);
                        } catch (directErr) {
                            console.log(`Direct sendMessage also failed: ${directErr?.message}`);
                            failed.push(participantId);
                        }
                    }
                } catch (sendErr) {
                    console.log(`Failed to send invite to ${participantId}:`, sendErr?.message);
                    failed.push(participantId);
                }
            }
            return { inviteLink, sent, failed };
        };

        // Try with autoSendInviteV4: true - this sends private invite if user has privacy settings
        try {
            result = await chat.addParticipants(validParticipants, { autoSendInviteV4: true });
            console.log('addParticipants result:', JSON.stringify(result));
            
            const checkRes = checkResult(result);
            
            if (checkRes.allAdded) {
                return res.json({ success: true, message: 'Participants added to group', result: checkRes.results });
            }

            const privacyBlockedResults = checkRes.results.filter(r => r.code === 403 && !r.inviteSent);
            if (privacyBlockedResults.length > 0) {
                try {
                    const inviteOutcome = await sendInviteLinkPrivately(privacyBlockedResults.map(r => r.participantId));
                    return res.json({
                        success: true,
                        message: 'Privacy settings prevent direct add; sent invite link privately',
                        inviteLinkSent: inviteOutcome.sent.length > 0,
                        inviteLinkFailed: inviteOutcome.failed.length > 0,
                        inviteLinkSentTo: inviteOutcome.sent,
                        inviteLinkFailedTo: inviteOutcome.failed,
                        result: checkRes.results
                    });
                } catch (inviteErr) {
                    return res.json({
                        success: true,
                        message: 'Privacy settings prevent direct add; attempted to send invite link privately but failed',
                        inviteLinkSent: false,
                        inviteLinkFailed: true,
                        details: inviteErr?.message,
                        result: checkRes.results
                    });
                }
            }

            if (checkRes.success) {
                const inviteSentList = checkRes.results.filter(r => r.inviteSent);
                const addedList = checkRes.results.filter(r => r.added);
                const failedList = checkRes.results.filter(r => !r.success);

                if (inviteSentList.length > 0 && failedList.length === 0) {
                    return res.json({
                        success: true,
                        message: 'Private invitation sent (user has privacy settings that prevent direct add)',
                        inviteSent: true,
                        result: checkRes.results
                    });
                }
                if (addedList.length > 0) {
                    return res.json({
                        success: true,
                        message: `Added ${addedList.length} participant(s)`,
                        result: checkRes.results
                    });
                }
            }
            
            // Check for specific error codes
            const failedResults = checkRes.results.filter(r => !r.success);
            if (failedResults.length > 0) {
                const firstFail = failedResults[0];
                return res.status(400).json({ 
                    error: firstFail.message || 'Failed to add participant',
                    code: firstFail.code,
                    result: checkRes.results 
                });
            }
        } catch (e) {
            console.log('addParticipants failed:', e?.message);
            lastError = e;
            
            // Check if it's a LID error - try to send invite link privately
            if (e?.message?.includes('Lid is missing')) {
                console.log('LID error detected, attempting to send invite link privately');
                try {
                    const inviteOutcome = await sendInviteLinkPrivately(validParticipants);
                    return res.json({
                        success: true,
                        message: 'Cannot add directly (WhatsApp LID issue); sent invite link privately',
                        inviteLinkSent: inviteOutcome.sent.length > 0,
                        inviteLinkFailed: inviteOutcome.failed.length > 0,
                        inviteLinkSentTo: inviteOutcome.sent,
                        inviteLinkFailedTo: inviteOutcome.failed
                    });
                } catch (inviteErr) {
                    console.log('Failed to send invite link:', inviteErr?.message);
                    return res.json({
                        success: true,
                        message: 'Cannot add directly (WhatsApp LID issue); attempted to send invite link privately but failed',
                        inviteLinkSent: false,
                        inviteLinkFailed: true,
                        details: inviteErr?.message
                    });
                }
            }
        }
        
        // All approaches failed
        const errorMsg = lastError?.message || 'Failed to add participants';
        console.error('Add participant failed:', errorMsg);
        res.status(500).json({ error: errorMsg });
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

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`WhatsApp Bridge running on port ${PORT}`);
    console.log('Waiting for WhatsApp authentication...');
});
