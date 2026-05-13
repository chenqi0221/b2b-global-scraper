const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const config = require('../../config/default');
const { createStatusRoutes } = require('./routes/status');
const { createContactsRoutes } = require('./routes/contacts');
const { createBroadcastRoutes } = require('./routes/broadcast');

function createApp(clientRef, clientState, logout, initClient) {
    const app = express();
    const server = http.createServer(app);
    const io = new Server(server);

    app.use(express.json({ limit: config.server.jsonLimit }));
    app.use(express.static(path.join(__dirname, '../../public')));
    app.use('/uploads', express.static(path.join(__dirname, '../../uploads')));

    createStatusRoutes(app, clientRef, clientState, io, logout, initClient);
    createContactsRoutes(app, clientRef, clientState);
    createBroadcastRoutes(app, clientRef, clientState, io);

    return { app, server, io };
}

module.exports = { createApp };
