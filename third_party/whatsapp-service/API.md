# API接口文档

## 状态查询

### GET /api/status

获取WhatsApp客户端状态

**响应:**

```json
{
    "status": "ready",
    "qr": null
}
```

### GET /api/daily-stats

获取每日发送统计

**响应:**

```json
{
    "date": "Mon May 11 2026",
    "sent": 15,
    "failed": 0,
    "paused": 0,
    "dailyMax": 30
}
```

### POST /api/set-account-level

设置账号安全级别

**请求:**

```json
{
    "level": "new"
}
```

**响应:**

```json
{
    "success": true,
    "level": "new"
}
```

## 联系人

### GET /api/chats

获取聊天列表

**响应:**

```json
{
    "chats": [
        {
            "id": "1234567890@c.us",
            "name": "张三",
            "isGroup": false,
            "lastMessage": "你好",
            "participants": 0
        }
    ]
}
```

### GET /api/contacts-list

获取所有联系人

**响应:**

```json
{
    "contacts": [
        {
            "id": "1234567890@c.us",
            "name": "张三",
            "number": "1234567890",
            "lid": null
        }
    ],
    "total": 1
}
```

### GET /api/export-contacts

导出联系人为CSV

**响应:** CSV文件下载

### GET /api/chat/:id

获取聊天记录

**响应:**

```json
{
    "chat": {
        "id": "1234567890@c.us",
        "name": "张三",
        "isGroup": false
    },
    "messages": [
        {
            "id": "...",
            "body": "你好",
            "type": "chat",
            "from": "1234567890@c.us",
            "fromMe": false,
            "timestamp": 1234567890
        }
    ]
}
```

## 广播

### POST /api/broadcast

启动广播

**请求:**

```json
{
    "message": ["消息模板1", "消息模板2"],
    "interval": 10000,
    "randomInterval": true,
    "randomizeMsg": true,
    "lengthRandomize": true,
    "simulateTyping": false,
    "simulateMouse": false,
    "respectHours": true,
    "randomPause": true,
    "excludeGroups": true,
    "personalize": false,
    "targetType": "chats",
    "accountLevel": "new"
}
```

**响应:**

```json
{
    "success": true,
    "progress": {
        "running": true,
        "current": 5,
        "total": 30,
        "results": [],
        "dailySent": 5,
        "dailyLimit": 30
    }
}
```

### GET /api/broadcast-status

获取广播状态

**响应:** 同POST /api/broadcast的progress字段

### POST /api/broadcast/stop

停止广播

**响应:**

```json
{
    "success": true
}
```
