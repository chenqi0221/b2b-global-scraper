const {
    getDailyStats,
    setAccountLevel,
} = require('../../services/rate-limiter');

function createStatusRoutes(
    app,
    clientRef,
    clientState,
    io,
    logout,
    initClient,
) {
    app.get('/api/status', (req, res) => {
        res.json({ status: clientState.status, qr: clientState.qr });
    });

    app.post('/api/connect', async (req, res) => {
        try {
            if (clientState.status === 'ready') {
                return res.json({
                    success: true,
                    message: 'Already connected',
                });
            }

            // 重置状态
            clientState.status = 'disconnected';
            clientState.qr = null;

            // 重新初始化客户端
            if (initClient && io) {
                initClient(io);
                res.json({
                    success: true,
                    message: 'Reinitializing client, please wait for QR code',
                });
            } else {
                res.json({
                    success: false,
                    error: 'Init function not available',
                });
            }
        } catch (e) {
            console.error('Connect error:', e);
            res.json({ success: false, error: e.message });
        }
    });

    app.post('/api/logout', async (req, res) => {
        try {
            await logout();
            res.json({ success: true, message: 'Logged out successfully' });
        } catch (e) {
            res.json({ success: false, error: e.message });
        }
    });

    app.get('/api/daily-stats', (req, res) => {
        res.json(getDailyStats());
    });

    app.post('/api/set-account-level', (req, res) => {
        const { level } = req.body;
        setAccountLevel(level);
        res.json({ success: true, level });
    });

    if (io) {
        io.on('connection', (socket) => {
            socket.emit('status', {
                status: clientState.status,
                qr: clientState.qr,
            });
        });
    }
}

module.exports = { createStatusRoutes };
