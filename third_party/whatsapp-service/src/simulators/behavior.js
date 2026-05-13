const { simulateHumanTyping } = require('./typing');
const { simulateHumanMouseMove } = require('./mouse');
const { simulateHumanScroll } = require('./scroll');

async function simulatePreSendBehavior(
    client,
    chatId,
    message,
    enableTyping = true,
) {
    if (!client || !client.pupPage) return;
    const page = client.pupPage;

    try {
        if (Math.random() < 0.4) {
            const viewport = await page.viewport();
            if (viewport) {
                await simulateHumanMouseMove(
                    page,
                    Math.random() * viewport.width,
                    Math.random() * viewport.height,
                );
                await new Promise((r) =>
                    setTimeout(r, 100 + Math.random() * 300),
                );
            }
        }

        await client.interface.openChatWindow(chatId);
        await new Promise((r) => setTimeout(r, 300 + Math.random() * 500));

        if (Math.random() < 0.3) {
            await simulateHumanScroll(page);
        }

        if (enableTyping && message && message.length > 5) {
            await simulateHumanTyping(page, message);
        }

        await new Promise((r) => setTimeout(r, 200 + Math.random() * 600));
    } catch (e) {
        console.error('Error in pre-send behavior simulation:', e.message);
    }
}

module.exports = { simulatePreSendBehavior };
