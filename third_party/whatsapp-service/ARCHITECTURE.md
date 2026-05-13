# 架构设计文档

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端界面                              │
│                    (public/index.html)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP / WebSocket
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     Express服务器                            │
│                   (src/server/app.js)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ /api/status │  │/api/contacts│  │   /api/broadcast    │  │
│  │   路由      │  │    路由     │  │      路由           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  WhatsApp    │ │  服务层   │ │   模拟器层    │
│   Client     │ │          │ │              │
│              │ │ Rate     │ │ 打字模拟      │
│ 初始化/事件   │ │ Limiter  │ │ 鼠标模拟      │
│ 联系人获取   │ │ Message  │ │ 滚动模拟      │
│ 消息发送     │ │ Randomizer│ │ 行为链       │
│              │ │ Anti-    │ │              │
│              │ │ Detection│ │              │
│              │ │ Broadcast│ │              │
└──────────────┘ └──────────┘ └──────────────┘
```

## 模块说明

### 1. 服务器层 (src/server/)

**app.js** - Express应用入口

- 创建HTTP服务器和Socket.IO
- 注册所有路由
- 提供静态文件服务

**routes/** - API路由分组

- `status.js` - 状态查询、每日统计
- `contacts.js` - 联系人获取、导出
- `broadcast.js` - 广播启动、停止、状态

### 2. 服务层 (src/services/)

**rate-limiter.js**

- 每日配额管理
- 三级账号安全级别
- 发送频率控制

**message-randomizer.js**

- 问候语去重
- 同义词替换
- 7种长度随机化策略

**anti-detection.js**

- 浏览器指纹伪装
- 10项反检测脚本注入

**broadcast.js**

- 广播状态管理
- 分批发送逻辑
- 间隔计算

### 3. 模拟器层 (src/simulators/)

**typing.js** - 模拟人类打字

- 逐字输入
- 随机延迟
- 模拟打错字

**mouse.js** - 模拟鼠标移动

- 贝塞尔曲线轨迹
- 随机偏移

**scroll.js** - 模拟页面滚动

- 随机距离和方向

**behavior.js** - 行为链

- 整合所有模拟动作
- 发送前完整流程

## 数据流

### 广播发送流程

```
用户请求 → broadcast路由 → broadcast服务 → rate-limiter检查
                                              ↓
                                    通过配额检查?
                                    是 → 计算间隔 → 发送消息
                                    否 → 返回限制错误
                                              ↓
                                    消息随机化(可选)
                                              ↓
                                    行为模拟(可选)
                                              ↓
                                    WhatsApp Client发送
                                              ↓
                                    更新统计 → 返回结果
```

## 依赖关系

```
web.js
  ├── config/default.js
  ├── src/server/app.js
  │     ├── src/server/routes/status.js
  │     │     └── src/services/rate-limiter.js
  │     ├── src/server/routes/contacts.js
  │     └── src/server/routes/broadcast.js
  │           ├── src/services/broadcast.js
  │           │     ├── src/services/rate-limiter.js
  │           │     ├── src/services/message-randomizer.js
  │           │     └── src/simulators/behavior.js
  │           └── src/services/rate-limiter.js
  └── src/services/anti-detection.js
```

## 关键设计决策

1. **模块化拆分**: 将3500+行的web.js拆分为独立模块，每个模块单一职责
2. **依赖注入**: 通过函数参数传递client和io，避免全局状态
3. **配置分离**: 将硬编码配置提取到config目录
4. **测试友好**: 每个服务独立导出，便于单元测试
