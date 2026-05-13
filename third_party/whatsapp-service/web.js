const { Client, LocalAuth } = require('./index');
const config = require('./config/default');
const { createApp } = require('./src/server/app');
const { injectAntiDetectionScripts } = require('./src/services/anti-detection');

const clientRef = { client: null };
const clientState = {
    status: 'disconnected',
    qr: null,
};

const clientConfig = {
    authStrategy: new LocalAuth({ dataPath: config.whatsapp.authPath }),
    puppeteer: {
        headless: config.whatsapp.headless,
        args: config.whatsapp.puppeteerArgs,
        timeout: config.whatsapp.timeout,
    },
};

let io = null;
let initRetryCount = 0;
const MAX_RETRY = 3;

function initClient(socketIo) {
    io = socketIo;
    if (clientRef.client) {
        try {
            clientRef.client.destroy();
        } catch (e) {
            // ignore
        }
        clientRef.client = null;
    }

    clientRef.client = new Client(clientConfig);

    clientRef.client.on('qr', (qr) => {
        clientState.qr = qr;
        clientState.status = 'qr';
        initRetryCount = 0;
        console.log('QR code received');
        if (io) io.emit('status', { status: 'qr', qr: clientState.qr });
    });

    clientRef.client.on('authenticated', () => {
        clientState.status = 'authenticated';
        initRetryCount = 0;
        console.log('Authenticated');
        if (io) io.emit('status', { status: 'authenticated', qr: null });
    });

    clientRef.client.on('ready', () => {
        clientState.status = 'ready';
        clientState.qr = null;
        initRetryCount = 0;
        console.log('\n\n===== WhatsApp Ready! =====\n');
        injectAntiDetectionScripts(clientRef.client);
        if (io) io.emit('status', { status: 'ready', qr: null });
    });

    clientRef.client.on('auth_failure', (msg) => {
        clientState.status = 'auth_failure';
        console.log('Auth failure:', msg);
        if (io)
            io.emit('status', {
                status: 'auth_failure',
                qr: null,
                error: msg,
            });
    });

    clientRef.client.on('disconnected', (reason) => {
        clientState.status = 'disconnected';
        console.log('Disconnected:', reason);
        if (io) io.emit('status', { status: 'disconnected', qr: null });
    });

    initializeWithRetry();
}

async function initializeWithRetry() {
    try {
        console.log(
            `Initializing client (attempt ${initRetryCount + 1}/${MAX_RETRY})...`,
        );
        await clientRef.client.initialize();
        console.log('Client initialization completed');
        initRetryCount = 0;
    } catch (error) {
        console.error('Error initializing client:', error.message);

        if (initRetryCount < MAX_RETRY) {
            initRetryCount++;
            const delay = initRetryCount * 3000;
            console.log(`Retrying in ${delay}ms...`);

            clientState.status = 'retrying';
            if (io)
                io.emit('status', {
                    status: 'retrying',
                    qr: null,
                    message: `初始化失败，${delay / 1000}秒后重试 (${initRetryCount}/${MAX_RETRY})...`,
                });

            setTimeout(() => {
                if (clientRef.client) {
                    initializeWithRetry();
                }
            }, delay);
        } else {
            console.error('Max retries reached. Giving up.');
            clientState.status = 'auth_failure';
            if (io)
                io.emit('status', {
                    status: 'auth_failure',
                    qr: null,
                    error: '初始化失败次数过多，请检查网络连接或点击"连接 WhatsApp"重试',
                });
        }
    }
}

async function logout() {
    if (clientRef.client) {
        try {
            await clientRef.client.destroy();
            console.log('Client destroyed');
        } catch (e) {
            console.error('Error destroying client:', e);
        }
        clientRef.client = null;
    }

    clientState.status = 'disconnected';
    clientState.qr = null;
    initRetryCount = 0;

    const fs = require('fs');
    const path = require('path');
    const authPath = path.resolve(config.whatsapp.authPath);

    if (fs.existsSync(authPath)) {
        try {
            fs.rmSync(authPath, { recursive: true, force: true });
            console.log('Auth data cleared');
        } catch (e) {
            console.error('Error clearing auth data:', e);
        }
    }

    if (io) {
        io.emit('status', { status: 'disconnected', qr: null });
    }
}

const {
    // eslint-disable-next-line no-unused-vars
    app,
    server,
    io: socketIo,
} = createApp(clientRef, clientState, logout, initClient);

initClient(socketIo);

module.exports = { logout, initClient };

server.listen(config.server.port, () => {
    console.log(
        `Web interface running at http://localhost:${config.server.port}`,
    );
});
