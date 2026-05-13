const { canSend, recordSend, getCurrentLimit } = require('./rate-limiter');
const { randomizeMessage } = require('./message-randomizer');
const { simulatePreSendBehavior } = require('../simulators/behavior');

let broadcastProgress = {
    running: false,
    current: 0,
    total: 0,
    results: [],
    message: null,
    interval: 10000,
};

function getBroadcastProgress() {
    return broadcastProgress;
}

function stopBroadcast() {
    broadcastProgress.running = false;
}

function calculateInterval(baseInterval, randomInterval, limit) {
    const forcedMinInterval = limit.minInterval;
    let actualInterval = baseInterval;

    if (randomInterval) {
        let randomMax = Math.max(baseInterval, forcedMinInterval) * 1.5;
        let randomMin = Math.max(forcedMinInterval * 0.8, baseInterval * 0.7);
        actualInterval = Math.floor(
            Math.random() * (randomMax - randomMin) + randomMin,
        );
        actualInterval = Math.max(actualInterval, forcedMinInterval);

        const now = new Date();
        const hour = now.getHours();
        const dayOfWeek = now.getDay();

        const isWorkHours =
            (hour >= 9 && hour < 12) || (hour >= 14 && hour < 18);
        const isLunchTime = hour >= 12 && hour < 14;
        const isEvening = hour >= 18 && hour < 22;
        const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;

        if (isWorkHours && !isWeekend) {
            actualInterval = Math.max(forcedMinInterval, actualInterval * 0.9);
        } else if (isLunchTime) {
            actualInterval = actualInterval * 1.3;
        } else if (isEvening) {
            actualInterval = actualInterval * 1.5;
        }

        if (isWeekend) {
            actualInterval = actualInterval * 1.3;
        }

        if (Math.random() < 0.05) {
            const breakTime = Math.floor(Math.random() * 30000 + 10000);
            return { interval: actualInterval, breakTime };
        }
    } else {
        actualInterval = Math.max(baseInterval, forcedMinInterval);
    }

    return {
        interval: Math.max(actualInterval, forcedMinInterval),
        breakTime: 0,
    };
}

async function runBroadcast(client, options, io) {
    const {
        targetItems,
        messages,
        interval = 10000,
        randomInterval = true,
        randomizeMsg = true,
        lengthRandomize = true,
        simulateTyping = false,
        simulateMouse = false,
        respectHours = true,
        randomPause = true,
        personalize = false,
    } = options;

    if (broadcastProgress.running) {
        throw new Error('Broadcast already running');
    }

    const limit = getCurrentLimit();

    broadcastProgress = {
        running: true,
        current: 0,
        total: targetItems.length,
        results: [],
        message: messages[0],
        interval,
        dailySent: 0,
        dailyLimit: limit.dailyMax,
        remaining: limit.dailyMax,
    };

    io.emit('broadcast-progress', broadcastProgress);

    let messageCount = 0;
    let batchCount = 0;

    for (const item of targetItems) {
        if (!broadcastProgress.running) break;

        // 广播当前正在发送的联系人
        io.emit('broadcast-current', {
            name: item.name,
            number: item.number,
            index: broadcastProgress.current + 1,
            total: broadcastProgress.total,
            status: 'sending',
        });

        const sendCheck = canSend();
        if (!sendCheck.allowed) {
            io.emit('broadcast-status', {
                type: 'daily_limit_reached',
                message: `Daily limit of ${limit.dailyMax} reached.`,
            });
            break;
        }

        if (respectHours) {
            const now = new Date();
            const hour = now.getHours();
            if (hour < 9 || hour >= 22) {
                const waitMinutes =
                    hour < 9 ? (9 - hour) * 60 : (24 - hour + 9) * 60;
                await new Promise((r) =>
                    setTimeout(r, waitMinutes * 60 * 1000),
                );
            }
        }

        if (
            randomPause &&
            messageCount > 0 &&
            messageCount % limit.batchSize === 0
        ) {
            batchCount++;
            const batchPauseTime =
                limit.batchPause + Math.floor(Math.random() * 30000);
            io.emit('broadcast-status', {
                type: 'batch_pause',
                batchCount,
                pauseSeconds: Math.round(batchPauseTime / 1000),
                remaining: sendCheck.remaining,
            });
            await new Promise((r) => setTimeout(r, batchPauseTime));
        }

        try {
            let selectedMessage =
                messages[Math.floor(Math.random() * messages.length)];
            let finalMessage =
                personalize && item.name
                    ? selectedMessage.replace(/{name}/g, item.name)
                    : selectedMessage;

            if (randomizeMsg) {
                const randomized = randomizeMessage(
                    finalMessage,
                    null,
                    lengthRandomize,
                );
                finalMessage = randomized.message;
            }

            let chatId = item.id;
            if (!chatId.includes('@')) {
                chatId = item.lid ? item.lid + '@lid' : item.number + '@c.us';
            }

            if (simulateTyping || simulateMouse) {
                try {
                    await simulatePreSendBehavior(
                        client,
                        chatId,
                        finalMessage,
                        simulateTyping,
                    );
                } catch (e) {
                    console.log('Behavior simulation failed:', e.message);
                }
            }

            await client.sendMessage(chatId, finalMessage);
            recordSend(true);
            messageCount++;

            broadcastProgress.results.push({
                name: item.name,
                status: 'success',
            });
            broadcastProgress.dailySent = sendCheck.sent + 1;
            broadcastProgress.remaining = Math.max(
                0,
                limit.dailyMax - broadcastProgress.dailySent,
            );

            // 广播成功状态
            io.emit('broadcast-current', {
                name: item.name,
                number: item.number,
                index: broadcastProgress.current + 1,
                total: broadcastProgress.total,
                status: 'success',
            });
        } catch (e) {
            recordSend(false);
            broadcastProgress.results.push({
                name: item.name,
                status: 'failed',
                error: e.message,
            });

            // 广播失败状态
            io.emit('broadcast-current', {
                name: item.name,
                number: item.number,
                index: broadcastProgress.current + 1,
                total: broadcastProgress.total,
                status: 'failed',
                error: e.message,
            });
        }

        broadcastProgress.current++;
        io.emit('broadcast-progress', broadcastProgress);

        const { interval: actualInterval, breakTime } = calculateInterval(
            interval,
            randomInterval,
            limit,
        );
        if (breakTime > 0) {
            await new Promise((r) => setTimeout(r, breakTime));
        }
        await new Promise((r) => setTimeout(r, Math.floor(actualInterval)));
    }

    broadcastProgress.running = false;
    io.emit('broadcast-progress', broadcastProgress);

    return {
        success: true,
        progress: broadcastProgress,
        dailyStats: { sent: messageCount },
    };
}

module.exports = {
    getBroadcastProgress,
    stopBroadcast,
    runBroadcast,
    calculateInterval,
};
