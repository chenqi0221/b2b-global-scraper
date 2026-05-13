async function simulateHumanTyping(page, text, options = {}) {
    if (!page || !text) return;

    const {
        minDelay = 50,
        maxDelay = 200,
        typoChance = 0.03,
        pauseChance = 0.15,
        pauseMin = 300,
        pauseMax = 800,
    } = options;

    try {
        await page.evaluate(() => {
            const input =
                document.querySelector(
                    'div[contenteditable="true"][data-tab="1"]',
                ) ||
                document.querySelector('div[contenteditable="true"]') ||
                document.querySelector(
                    '[data-testid="conversation-compose-box-input"]',
                );
            if (input) {
                input.focus();
                input.click();
            }
        });

        await new Promise((r) => setTimeout(r, 100 + Math.random() * 200));
        await page.keyboard.press('Control+a');
        await new Promise((r) => setTimeout(r, 50 + Math.random() * 100));
        await page.keyboard.press('Delete');
        await new Promise((r) => setTimeout(r, 50 + Math.random() * 100));

        for (let i = 0; i < text.length; i++) {
            const char = text[i];

            if (Math.random() < pauseChance && i > 0 && i < text.length - 1) {
                const pauseTime =
                    pauseMin + Math.random() * (pauseMax - pauseMin);
                await new Promise((r) => setTimeout(r, pauseTime));
            }

            if (Math.random() < typoChance && /[a-zA-Z]/.test(char)) {
                const nearbyKeys = {
                    a: 's',
                    s: 'a',
                    d: 's',
                    f: 'd',
                    g: 'f',
                    h: 'g',
                    j: 'h',
                    k: 'j',
                    l: 'k',
                    q: 'w',
                    w: 'q',
                    e: 'w',
                    r: 'e',
                    t: 'r',
                    y: 't',
                    u: 'y',
                    i: 'u',
                    o: 'i',
                    p: 'o',
                };
                const typoChar = nearbyKeys[char.toLowerCase()];
                if (typoChar) {
                    await page.keyboard.type(typoChar, {
                        delay: minDelay + Math.random() * (maxDelay - minDelay),
                    });
                    await new Promise((r) =>
                        setTimeout(r, 100 + Math.random() * 200),
                    );
                    await page.keyboard.press('Backspace');
                    await new Promise((r) =>
                        setTimeout(r, 80 + Math.random() * 150),
                    );
                }
            }

            const delay = minDelay + Math.random() * (maxDelay - minDelay);
            await page.keyboard.type(char, { delay });
        }
    } catch (e) {
        console.error('Error during human typing simulation:', e.message);
    }
}

module.exports = { simulateHumanTyping };
