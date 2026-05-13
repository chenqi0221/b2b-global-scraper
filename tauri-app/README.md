# B2B Global 获客系统（Tauri + React）

## 开发方式

- **`npm run web`** 或 **`npm run dev`**：只启动 Vite，在**系统浏览器**里调试前端（**不会出现** Tauri 桌面窗口）。
- **`npm run desktop`** 或 **`npm run tauri:dev`**：启动 **Tauri 桌面窗口**（内嵌 WebView），与正式桌面体验一致；`tauri.conf.json` 里已把默认窗口设为较大尺寸。

后端 API 需按项目主 README 另行启动。

### 桌面正式包：状态同步失败 / Failed to fetch

1. **CORS**：生产 WebView 源常为 `https://tauri.localhost:<随机端口>`，后端已用 `allow_origin_regex` 放行；请**重新打包**并运行**新** `app.exe`（并确保本机跑的是**更新后的** `backend/main.py`）。
2. **Python 未拉起**：资源管理器双击 exe 时 **PATH 可能不含 `python`**。壳层已优先尝试 Windows **`py -3`**，再回退 **`python`**；请安装 Python / Launcher，并在仓库根装好依赖（见下）。
3. **仓库根路径**：API 进程需在含 `backend/main.py` 的目录下启动。已按 `app.exe` 位置自动推断 `…/tauri-app/src-tauri/target/release` → 仓库根；若仅拷贝 exe 到别处，请设置环境变量 **`B2B_REPO_ROOT`** 指向完整仓库根后再启动。
4. **依赖**：在仓库根执行 `pip install -r backend/requirements.txt`（或你的虚拟环境内）。

### 一键执行（本机）

在仓库根目录 **CMD** 中执行（勿在 PowerShell 里用 `call` 混用路径时出错，可直接双击或在 CMD 里运行）：

```bat
scripts\run_all.bat
```

顺序：`pytest` → `tauri-app` 下 `npm run build` → `cargo check` → `npm run package`（NSIS 安装包）。  
若只需验证、不打包：`scripts\smoke_test.bat`。

### 打包（Windows 桌面安装包）

仓库根执行 `scripts\package_tauri.bat`，或在 `tauri-app` 目录执行 `npm run package`（内部为 `npm run build` + `tauri build`，默认产出 **NSIS 安装程序**，在 `src-tauri\target\release\bundle\nsis\`；可执行文件在 `target\release\app.exe`）。

PowerShell 切换目录请用 `cd E:\路径\tauri-app`，不要使用 cmd 的 `cd /d`（PowerShell 会报错）。

如需 **MSI**（WiX），请把仓库放在仅 ASCII 的路径下并把 `tauri.conf.json` 里 `bundle.targets` 改为包含 `"msi"`；中文路径下 WiX `light.exe` 常失败。

---

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
