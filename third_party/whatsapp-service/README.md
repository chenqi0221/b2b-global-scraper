# WhatsApp自动化库 v2.0

基于 whatsapp-web.js 的 WhatsApp Web 自动化工具，集成防检测、频率限制、消息随机化等高级功能。

## 快速开始

```bash
npm install
node web.js
```

访问 http://localhost:3003 扫码登录。

## 主要功能

- 群发消息（支持多模板随机选择）
- 账号安全级别控制（新账号/稳定账号/老账号）
- 消息内容随机化（7种策略）
- 人类行为模拟（打字、鼠标移动）
- 浏览器指纹伪装（10项反检测）
- 发送时间模拟人类作息
- 每日发送配额限制
- 联系人管理与导出

## 项目结构

```
whatsapp-web.js/
├── web.js                    # 入口文件（精简版）
├── config/
│   ├── default.js            # 默认配置
│   └── rate-limits.js        # 频率限制配置
├── src/
│   ├── server/
│   │   ├── app.js            # Express应用
│   │   └── routes/           # API路由
│   │       ├── status.js
│   │       ├── contacts.js
│   │       └── broadcast.js
│   ├── services/
│   │   ├── rate-limiter.js   # 频率限制服务
│   │   ├── message-randomizer.js
│   │   ├── anti-detection.js
│   │   └── broadcast.js      # 广播业务逻辑
│   ├── simulators/
│   │   ├── typing.js         # 打字模拟
│   │   ├── mouse.js          # 鼠标模拟
│   │   ├── scroll.js         # 滚动模拟
│   │   └── behavior.js       # 行为链
│   └── utils/
├── tests/
│   └── unit/                 # 单元测试
├── public/
│   └── index.html            # 前端界面
└── CHANGELOG-v2.0.md
```

## 测试

```bash
npx mocha tests/unit/*.test.js
```

## 文档

- [CHANGELOG-v2.0.md](CHANGELOG-v2.0.md) - 更新说明
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计
- [API.md](API.md) - API接口文档
- [DEVELOPMENT.md](DEVELOPMENT.md) - 开发指南

## 许可证

MIT
