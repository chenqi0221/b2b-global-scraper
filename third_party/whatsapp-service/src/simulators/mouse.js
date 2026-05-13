async function simulateHumanMouseMove(page, targetX, targetY) {
    if (!page) return;

    try {
        const currentPos = await page.evaluate(() => ({
            x: window.mouseX || 0,
            y: window.mouseY || 0,
        }));

        const startX = currentPos.x || Math.random() * 500;
        const startY = currentPos.y || Math.random() * 500;

        const cp1x =
            startX + (targetX - startX) * 0.3 + (Math.random() - 0.5) * 100;
        const cp1y =
            startY + (targetY - startY) * 0.3 + (Math.random() - 0.5) * 100;
        const cp2x =
            startX + (targetX - startX) * 0.7 + (Math.random() - 0.5) * 100;
        const cp2y =
            startY + (targetY - startY) * 0.7 + (Math.random() - 0.5) * 100;

        const steps = 15 + Math.floor(Math.random() * 20);

        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            const x =
                Math.pow(1 - t, 3) * startX +
                3 * Math.pow(1 - t, 2) * t * cp1x +
                3 * (1 - t) * Math.pow(t, 2) * cp2x +
                Math.pow(t, 3) * targetX;
            const y =
                Math.pow(1 - t, 3) * startY +
                3 * Math.pow(1 - t, 2) * t * cp1y +
                3 * (1 - t) * Math.pow(t, 2) * cp2y +
                Math.pow(t, 3) * targetY;

            await page.mouse.move(x, y);
            await new Promise((r) => setTimeout(r, 3 + Math.random() * 8));
        }
    } catch (e) {
        console.error('Error during mouse move simulation:', e.message);
    }
}

module.exports = { simulateHumanMouseMove };
