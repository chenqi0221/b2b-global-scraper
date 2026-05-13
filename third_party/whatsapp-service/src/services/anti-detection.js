async function injectAntiDetectionScripts(client) {
    if (!client || !client.pupPage) return;

    try {
        await client.pupPage.evaluateOnNewDocument(() => {
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                configurable: true,
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        name: 'Chrome PDF Viewer',
                        filename: 'internal-pdf-viewer',
                        description: 'Portable Document Format',
                    },
                    {
                        name: 'Chromium PDF Viewer',
                        filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                        description: 'Portable Document Format',
                    },
                    {
                        name: 'Native Client',
                        filename: 'internal-nacl-plugin',
                        description: 'Native Client module',
                    },
                ],
                configurable: true,
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
                configurable: true,
            });

            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 4,
                configurable: true,
            });

            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8,
                configurable: true,
            });

            if (!window.chrome) {
                window.chrome = { runtime: {}, app: { isInstalled: false } };
            }

            delete navigator.__proto__.webdriver;

            if (window.Notification) {
                Object.defineProperty(Notification, 'permission', {
                    get: () => 'default',
                    configurable: true,
                });
            }

            if (navigator.permissions) {
                const originalQuery = navigator.permissions.query;
                navigator.permissions.query = function (parameters) {
                    if (parameters.name === 'notifications') {
                        return Promise.resolve({
                            state: 'default',
                            onchange: null,
                        });
                    }
                    return originalQuery.call(this, parameters);
                };
            }

            window.mouseX = 0;
            window.mouseY = 0;
            document.addEventListener('mousemove', (e) => {
                window.mouseX = e.clientX;
                window.mouseY = e.clientY;
            });
        });
    } catch (e) {
        console.error('Failed to inject anti-detection scripts:', e.message);
    }
}

module.exports = { injectAntiDetectionScripts };
