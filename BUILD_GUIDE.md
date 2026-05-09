# Google Maps爬虫项目打包指南

本指南将帮助您打包整个Google Maps爬虫项目，包括爬取功能和WhatsApp工具，以便在其他Windows电脑上运行。

## 1. 准备工作

### 1.1 安装Python和PyInstaller

1. 从 [Python官网](https://www.python.org/downloads/windows/) 下载并安装Python 3.10或更高版本
2. 确保勾选 "Add Python to PATH" 选项
3. 安装PyInstaller：
   ```cmd
   python -m pip install pyinstaller
   ```

### 1.2 安装项目依赖

1. 打开命令提示符（CMD）
2. 切换到项目目录：
   ```cmd
   cd /d E:\办公小程序\google-maps-scraper
   ```
3. 安装所有依赖：
   ```cmd
   python -m pip install -r requirements.txt
   ```
4. 安装额外依赖：
   ```cmd
   python -m pip install pandas gspread oauth2client openpyxl playwright ttkbootstrap python-dotenv
   ```
5. 安装Playwright浏览器：
   ```cmd
   python -m playwright install
   ```

## 2. 创建PyInstaller配置文件

创建一个名为 `build.spec` 的文件，内容如下：

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 包含所有必要的文件
datas = [
    ('pages/*', 'pages'),
    ('assets/*', 'assets'),
    ('.env', '.'),
    ('app_config.json', '.'),
    ('keywords_library.json', '.'),
    ('client_secret.json', '.'),
    ('token.json', '.'),
]

# 隐藏控制台窗口（仅GUI程序）
options = [
    '--windowed',
    '--onefile',
    '--name=GoogleMapsScraper',
    '--icon=assets/icon.ico',  # 如果有图标文件
    '--add-data=pages/*;pages',
    '--add-data=assets/*;assets',
    '--add-data=.env;.',
    '--add-data=app_config.json;.',
    '--add-data=keywords_library.json;.',
    '--add-data=client_secret.json;.',
    '--add-data=token.json;.',
]

# 主程序入口
a = Analysis(['gui_scraper.py'],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=[
                 'asyncio',
                 'pandas',
                 'gspread',
                 'oauth2client',
                 'openpyxl',
                 'playwright',
                 'ttkbootstrap',
                 'python_dotenv',
                 'ai_generator',
                 'google_maps_scraper',
                 'google_sheets_service',
                 'sheet_aggregator',
                 'data',
             ],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# GUI程序设置
executable = EXE(pyz,
              a.scripts,
              [],
              exclude_binaries=True,
              name='GoogleMapsScraper',
              debug=False,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              console=False,  # 隐藏控制台窗口
              disable_windowed_traceback=False,
              argv_emulation=False,
              target_arch=None,
              codesign_identity=None,
              entitlements_file=None,
              icon='assets/icon.ico')

# 收集所有文件
coll = COLLECT(executable,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='GoogleMapsScraper')
```

## 3. 打包主GUI程序

1. 确保 `build.spec` 文件在项目根目录下
2. 运行打包命令：
   ```cmd
   pyinstaller build.spec
   ```
3. 打包完成后，可执行文件将生成在 `dist` 目录中

## 4. 打包WhatsApp工具（可选）

如果您也想单独打包WhatsApp工具，可以创建一个单独的配置文件 `build_whatsapp.spec`：

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

datas = [
    ('.env', '.'),
]

a = Analysis(['whatsapp_contacts.py'],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=[
                 'pandas',
                 'gspread',
                 'oauth2client',
                 'openpyxl',
             ],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

executable = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              [],
              name='WhatsAppContacts',
              debug=False,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              upx_exclude=[],
              runtime_tmpdir=None,
              console=True,  # WhatsApp工具需要控制台输出
              disable_windowed_traceback=False,
              argv_emulation=False,
              target_arch=None,
              codesign_identity=None,
              entitlements_file=None)
```

运行打包命令：
```cmd
pyinstaller build_whatsapp.spec
```

## 5. 使用打包后的程序

### 5.1 主GUI程序

1. 进入 `dist` 目录
2. 运行 `GoogleMapsScraper.exe`
3. 程序将自动加载配置文件
4. 您可以开始使用Google Maps爬虫功能

### 5.2 WhatsApp工具

1. 进入 `dist` 目录
2. 打开命令提示符（CMD）
3. 运行：
   ```cmd
   WhatsAppContacts.exe --help
   ```
4. 按照提示使用WhatsApp联系人功能

## 6. 注意事项

1. **文件路径**：确保所有必要的配置文件都在程序同目录下
2. **浏览器依赖**：打包后的程序可能需要Playwright浏览器，确保已安装
3. **凭证文件**：确保 `client_secret.json` 和 `token.json` 文件存在
4. **配置文件**：首次运行前，确保 `.env` 文件已正确配置
5. **权限问题**：以管理员身份运行程序，避免权限问题

## 7. 常见问题解决

### 问题1：程序无法启动

**解决方法**：
- 检查是否缺少必要的配置文件
- 检查是否已安装Playwright浏览器
- 查看 `dist` 目录下是否有错误日志文件

### 问题2：无法连接到Google Sheets

**解决方法**：
- 检查 `client_secret.json` 和 `token.json` 文件是否存在
- 确保 `token.json` 文件未过期
- 重新生成授权令牌

### 问题3：缺少依赖库

**解决方法**：
- 确保已安装所有依赖
- 在 `build.spec` 文件中添加缺失的 `hiddenimports`

## 8. 便携式使用

1. 将 `dist` 目录复制到U盘或移动硬盘
2. 在目标电脑上运行 `GoogleMapsScraper.exe`
3. 无需安装Python或其他依赖

## 9. 高级配置

### 9.1 自定义图标

1. 准备一个 `.ico` 图标文件
2. 放置在 `assets` 目录下
3. 在 `build.spec` 文件中设置 `icon='assets/icon.ico'`

### 9.2 多文件打包

如果您希望生成单个可执行文件，修改 `build.spec` 文件：

```python
# 修改 executable 部分
options = [
    '--onefile',  # 生成单个文件
    # 其他选项...
]
```

### 9.3 保留控制台窗口

如果您需要查看程序输出，修改 `build.spec` 文件：

```python
# 修改 executable 部分
console=True  # 显示控制台窗口
```

## 10. 测试打包后的程序

1. 在另一台Windows电脑上测试
2. 确保所有功能正常工作
3. 检查日志文件，解决任何错误
4. 优化打包配置

## 11. 版本控制

1. 定期更新打包配置
2. 记录每个版本的更改
3. 备份打包后的程序

通过以上步骤，您可以成功打包整个Google Maps爬虫项目，包括爬取功能和WhatsApp工具，以便在其他Windows电脑上运行。