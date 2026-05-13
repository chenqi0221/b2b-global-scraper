async function simulateHumanScroll(page) {
    if (!page) return;

    try {
        const scrollAmount = 100 + Math.floor(Math.random() * 300);
        const direction = Math.random() < 0.7 ? -1 : 1;

        await page.evaluate(
            (amount, dir) => {
                window.scrollBy({ top: amount * dir, behavior: 'smooth' });
            },
            scrollAmount,
            direction,
        );

        await new Promise((r) => setTimeout(r, 200 + Math.random() * 500));
    } catch (e) {
        console.error('Error during scroll simulation:', e.message);
    }
}

module.exports = { simulateHumanScroll };
