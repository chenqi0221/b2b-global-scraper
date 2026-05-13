const { Client, LocalAuth } = require('./index');

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: false,
    },
});

client.on('ready', async () => {
    console.log('Client is ready!');

    const chats = await client.getChats();
    console.log(`Total chats: ${chats.length}`);

    const message = '您好！这是测试消息。';

    let sentCount = 0;
    let failCount = 0;

    for (const chat of chats) {
        try {
            const chatId = chat.id._serialized;
            const chatName = chat.name || chatId;

            if (!chatId || chat.isGroup) {
                console.log(`Skipping group or invalid chat: ${chatName}`);
                continue;
            }

            await client.sendMessage(chatId, message);
            sentCount++;
            console.log(`Sent to ${chatName} (${sentCount})`);

            await new Promise((resolve) => setTimeout(resolve, 10000));
        } catch (error) {
            failCount++;
            console.error(
                `Failed to send to ${chat.name || 'unknown'}: ${error.message}`,
            );
        }
    }

    console.log(`\nCompleted! Sent: ${sentCount}, Failed: ${failCount}`);
});

client.on('message', async (msg) => {
    console.log('MESSAGE RECEIVED', msg.body);
});

client.on('disconnected', (reason) => {
    console.log('Client was logged out', reason);
});

client.initialize();
