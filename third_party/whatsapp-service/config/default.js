module.exports = {
    server: {
        port: process.env.PORT || 3003,
        jsonLimit: '50mb',
    },
    whatsapp: {
        authPath: './.wwebjs_auth_v2',
        headless: true,
        timeout: 120000,
        puppeteerArgs: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-blink-features=AutomationControlled',
            '--lang=en-US,en',
            '--window-size=1920,1080',
        ],
    },
    broadcast: {
        defaultInterval: 10000,
        randomInterval: true,
        respectHours: true,
        randomPause: true,
        excludeGroups: true,
    },
};
