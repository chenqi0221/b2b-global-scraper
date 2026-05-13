function createContactsRoutes(app, clientRef, clientState) {
    app.get('/api/chats', async (req, res) => {
        if (!clientRef.client || clientState.status !== 'ready') {
            return res.json({ chats: [] });
        }
        try {
            const chats = await clientRef.client.getChats();
            const chatList = chats.map((chat) => ({
                id: chat.id._serialized,
                name: chat.name,
                isGroup: chat.isGroup,
                lastMessage: chat.lastMessage?.body || '',
                participants: chat.participants?.length || 0,
            }));
            res.json({ chats: chatList });
        } catch (e) {
            res.json({ chats: [], error: e.message });
        }
    });

    app.get('/api/contacts-list', async (req, res) => {
        if (!clientRef.client || clientState.status !== 'ready') {
            return res.json({ contacts: [], error: 'Client not ready' });
        }
        try {
            const contactsData = await clientRef.client.pupPage.evaluate(
                async () => {
                    let contacts = [];
                    if (window.require) {
                        try {
                            const Collections =
                                window.require('WAWebCollections');
                            if (Collections && Collections.Contact) {
                                if (Collections.Contact._index) {
                                    const allContacts = Object.values(
                                        Collections.Contact._index,
                                    );
                                    contacts = allContacts.filter((c) => {
                                        try {
                                            const attrs =
                                                c.attributes ||
                                                (c.serialize
                                                    ? c.serialize()
                                                    : c);
                                            return attrs && attrs.phoneNumber;
                                        } catch (e) {
                                            return false;
                                        }
                                    });
                                }
                                if (
                                    (!contacts || contacts.length === 0) &&
                                    Collections.Contact.findAll
                                ) {
                                    contacts =
                                        await Collections.Contact.findAll();
                                }
                            }
                        } catch (e) {
                            console.log('Error WAWebCollections:', e.message);
                        }
                    }

                    const result = [];
                    const seenNumbers = new Set();

                    for (const c of contacts || []) {
                        try {
                            let attrs =
                                c.attributes ||
                                (c.serialize ? c.serialize() : c);
                            let number =
                                attrs.phone ||
                                attrs.phoneNumber ||
                                attrs.id?.user ||
                                attrs.userid;
                            if (
                                typeof number === 'object' &&
                                number !== null &&
                                number.user
                            ) {
                                number = number.user;
                            }
                            if (!number && attrs.id && attrs.id._serialized) {
                                number = attrs.id._serialized.split('@')[0];
                            }
                            if (
                                !number ||
                                typeof number !== 'string' ||
                                number.length <= 5
                            )
                                continue;
                            if (seenNumbers.has(number)) continue;
                            seenNumbers.add(number);

                            result.push({
                                number,
                                name:
                                    attrs.displayName ||
                                    attrs.pushname ||
                                    attrs.shortName ||
                                    attrs.name ||
                                    number,
                                isMe: attrs.isMe,
                                lid: attrs.id?.user || null,
                                id: attrs.id?._serialized || null,
                            });
                        } catch (e) {
                            console.log('Error processing contact:', e.message);
                        }
                    }
                    return { contacts: result };
                },
            );

            const contactList = contactsData.contacts
                .filter((c) => !c.isMe)
                .map((c) => ({
                    id: c.number + '@c.us',
                    name: c.name,
                    number: c.number,
                    lid: c.lid || null,
                }));

            res.json({ contacts: contactList, total: contactList.length });
        } catch (e) {
            console.log('API Error:', e.message);
            res.json({ contacts: [], error: e.message });
        }
    });

    app.get('/api/export-contacts', async (req, res) => {
        if (!clientRef.client || clientState.status !== 'ready') {
            return res.json({ error: 'Client not ready' });
        }
        try {
            const chats = await clientRef.client.getChats();
            const contacts = [];
            const seenNumbers = new Set();

            for (const chat of chats) {
                if (chat.isGroup) continue;
                let number = null;
                if (chat.id?.user) {
                    number = chat.id.user;
                } else if (chat.id?._serialized) {
                    const match = chat.id._serialized.match(/^(\d+)@/);
                    if (match) number = match[1];
                }
                if (number && !seenNumbers.has(number) && number.length > 5) {
                    seenNumbers.add(number);
                    contacts.push({ number, name: chat.name || number });
                }
            }

            let csv = '\uFEFF手机号,姓名\n';
            contacts.forEach((c) => {
                csv += `${c.number},${c.name}\n`;
            });

            res.setHeader('Content-Type', 'text/csv;charset=utf-8');
            res.setHeader(
                'Content-Disposition',
                'attachment; filename=contacts.csv',
            );
            res.send(csv);
        } catch (e) {
            res.json({ error: e.message });
        }
    });

    app.get('/api/chat/:id', async (req, res) => {
        if (!clientRef.client || clientState.status !== 'ready') {
            return res.json({ error: 'Client not ready' });
        }
        try {
            const chat = await clientRef.client.getChatById(req.params.id);
            const messages = await chat.fetchMessages({ limit: 50 });
            res.json({
                chat: {
                    id: chat.id._serialized,
                    name: chat.name,
                    isGroup: chat.isGroup,
                },
                messages: messages.map((m) => ({
                    id: m.id._serialized,
                    body: m.body,
                    type: m.type,
                    from: m.from,
                    fromMe: m.fromMe,
                    timestamp: m.timestamp,
                })),
            });
        } catch (e) {
            res.json({ error: e.message });
        }
    });
}

module.exports = { createContactsRoutes };
