const {
    getBroadcastProgress,
    stopBroadcast,
    runBroadcast,
} = require('../../services/broadcast');
const { canSend, setAccountLevel } = require('../../services/rate-limiter');

function createBroadcastRoutes(app, clientRef, clientState, io) {
    app.get('/api/broadcast-status', (req, res) => {
        res.json(getBroadcastProgress());
    });

    app.post('/api/broadcast/stop', (req, res) => {
        stopBroadcast();
        res.json({ success: true });
    });

    app.post('/api/broadcast', async (req, res) => {
        const {
            message,
            interval = 10000,
            randomInterval = true,
            randomizeMsg = true,
            lengthRandomize = true,
            simulateTyping = false,
            simulateMouse = false,
            respectHours = true,
            randomPause = true,
            excludeGroups = true,
            personalize,
            targetType = 'chats',
            manualNumbers,
            accountLevel = 'new',
        } = req.body;

        setAccountLevel(accountLevel);

        let messages = [];
        if (Array.isArray(message)) {
            messages = message;
        } else if (typeof message === 'string' && message.includes('\n')) {
            messages = message
                .split('\n')
                .map((line) => line.trim())
                .filter((line) => line.length > 0);
        } else {
            messages = [message];
        }

        if (!clientRef.client || clientState.status !== 'ready') {
            return res.json({ success: false, error: 'Client not ready' });
        }

        const sendCheck = canSend();
        if (!sendCheck.allowed) {
            return res.json({
                success: false,
                error: `Daily limit reached (${sendCheck.dailyMax}).`,
            });
        }

        try {
            let targetItems = [];

            if (targetType === 'manual' && manualNumbers) {
                const numbers = manualNumbers
                    .split(/[,\n]/)
                    .map((n) => n.trim())
                    .filter((n) => n.length > 0);
                targetItems = numbers.map((num) => ({
                    id: num + '@c.us',
                    name: num,
                    number: num,
                }));
            } else {
                const chats = await clientRef.client.getChats();
                const filteredChats = chats.filter((chat) => {
                    if (excludeGroups && chat.isGroup) return false;
                    if (targetType === 'groups') return chat.isGroup;
                    if (targetType === 'private') return !chat.isGroup;
                    return true;
                });

                targetItems = filteredChats.map((chat) => {
                    const number =
                        chat.id?.user ||
                        chat.id?._serialized?.split('@')[0] ||
                        '';
                    return {
                        id: chat.id._serialized,
                        name: chat.name || number,
                        number,
                        lid: null,
                    };
                });
            }

            const result = await runBroadcast(
                clientRef.client,
                {
                    targetItems,
                    messages,
                    interval,
                    randomInterval,
                    randomizeMsg,
                    lengthRandomize,
                    simulateTyping,
                    simulateMouse,
                    respectHours,
                    randomPause,
                    personalize,
                },
                io,
            );

            res.json(result);
        } catch (e) {
            res.json({ success: false, error: e.message });
        }
    });
}

module.exports = { createBroadcastRoutes };
