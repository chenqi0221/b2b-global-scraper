# 开发指南

## 环境搭建

```bash
# 克隆项目
git clone <repo-url>
cd whatsapp-web.js

# 安装依赖
npm install

# 运行测试
npx mocha tests/unit/*.test.js

# 启动服务
node web.js
```

## 代码规范

### 文件组织

- 每个模块一个文件
- 文件名使用kebab-case
- 测试文件与源文件同名，后缀`.test.js`

### 导出规范

```javascript
// 服务模块
module.exports = {
    functionName,
    anotherFunction,
};

// 路由模块
module.exports = { createRouteName };
```

### 错误处理

```javascript
try {
    await someAsyncOperation();
} catch (e) {
    console.error('Operation failed:', e.message);
}
```

## 添加新功能

### 1. 添加新服务

在 `src/services/` 创建新文件：

```javascript
// src/services/my-service.js
function myFunction() {
    // 实现
}

module.exports = { myFunction };
```

### 2. 添加新路由

在 `src/server/routes/` 创建新文件：

```javascript
// src/server/routes/my-route.js
function createMyRoutes(app, client) {
    app.get('/api/my-endpoint', async (req, res) => {
        // 实现
    });
}

module.exports = { createMyRoutes };
```

在 `src/server/app.js` 注册：

```javascript
const { createMyRoutes } = require('./routes/my-route');
// ...
createMyRoutes(app, client);
```

### 3. 添加测试

在 `tests/unit/` 创建测试文件：

```javascript
// tests/unit/my-service.test.js
const assert = require('assert');
const { myFunction } = require('../../src/services/my-service');

describe('My Service', () => {
    it('should do something', () => {
        const result = myFunction();
        assert.strictEqual(result, expected);
    });
});
```

## 测试指南

### 运行测试

```bash
# 所有测试
npx mocha tests/unit/*.test.js

# 单个测试文件
npx mocha tests/unit/rate-limiter.test.js

# 带覆盖率
npx nyc mocha tests/unit/*.test.js
```

### 测试规范

- 每个测试文件对应一个源文件
- 使用describe分组
- 测试名描述行为，不是实现
- 避免测试随机性（使用固定种子或mock）

## 调试

### 日志输出

```javascript
console.log('Debug info:', variable);
console.error('Error:', error.message);
```

### 使用断点

```bash
node --inspect web.js
```

然后在Chrome DevTools中连接。

## Git提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
refactor: 重构（无功能变化）
test: 测试相关
chore: 构建/工具相关
```

示例：

```bash
git commit -m "feat: add new anti-detection strategy"
```
