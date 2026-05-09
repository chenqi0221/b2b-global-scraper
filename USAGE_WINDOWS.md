# WhatsApp通讯录批量添加工具 - Windows使用指南

本指南将帮助您在Windows电脑上运行WhatsApp通讯录批量添加工具。

## 1. 安装Python

### 方法1：从Python官网下载安装（推荐）

1. 访问 [Python官网](https://www.python.org/downloads/windows/)
2. 下载最新的Python安装包（选择"Windows installer (64-bit)"）
3. 运行安装程序
4. **重要**：勾选 "Add Python to PATH" 选项
5. 点击 "Install Now" 完成安装
6. 安装完成后，打开命令提示符（CMD），输入 `python --version` 验证安装成功

### 方法2：使用Microsoft Store安装

1. 打开Microsoft Store
2. 搜索 "Python"
3. 选择Python 3.10或更高版本
4. 点击 "获取" 安装
5. 安装完成后，打开命令提示符（CMD），输入 `python --version` 验证安装成功

## 2. 安装依赖库

1. 打开命令提示符（CMD）
2. 切换到工具所在目录：
   ```cmd
   cd /d E:\办公小程序\google-maps-scraper
   ```
3. 安装所需依赖：
   ```cmd
   python -m pip install pandas gspread oauth2client openpyxl
   ```

## 3. 配置工具

1. 运行配置命令：
   ```cmd
   python whatsapp_contacts.py --config
   ```
2. 根据提示输入配置信息：
   - Google凭证文件路径
   - 默认表格ID
   - 默认工作表名称
   - 默认姓名列名称
   - 默认电话号码列名称

## 4. 运行工具

### 从本地文件读取数据

```cmd
# 从CSV文件读取数据
python whatsapp_contacts.py contacts.csv

# 从Excel文件读取数据
python whatsapp_contacts.py contacts.xlsx

# 指定姓名列和电话列
python whatsapp_contacts.py contacts.csv --name-col 姓名 --phone-col 电话
```

### 从Google Sheets读取数据

```cmd
# 使用默认配置
python whatsapp_contacts.py YOUR_GOOGLE_SHEETS_ID

# 指定工作表
python whatsapp_contacts.py YOUR_GOOGLE_SHEETS_ID --worksheet Sheet2

# 指定列名称
python whatsapp_contacts.py YOUR_GOOGLE_SHEETS_ID --name-col CustomerName --phone-col PhoneNumber
```

## 5. 便携式使用方法（无需安装）

如果您需要在多台电脑上使用，而不想在每台电脑上安装Python，可以使用便携式Python：

1. 下载 [Portable Python](https://portablepython.com/)
2. 将Portable Python解压缩到U盘或移动硬盘
3. 将工具文件复制到同一个U盘
4. 使用便携式Python运行工具：
   ```cmd
   "D:\Portable Python\python.exe" whatsapp_contacts.py contacts.csv
   ```

## 6. 常见问题解决

### 问题1：找不到Python命令

**解决方法**：
- 检查是否已安装Python
- 确保安装时勾选了 "Add Python to PATH"
- 尝试使用 `py` 命令代替 `python`：
  ```cmd
  py -m pip install pandas gspread oauth2client openpyxl
  py whatsapp_contacts.py contacts.csv
  ```

### 问题2：缺少依赖库

**解决方法**：
- 确保已安装所有依赖：
  ```cmd
  python -m pip install pandas gspread oauth2client openpyxl
  ```

### 问题3：Google Sheets访问失败

**解决方法**：
- 确保Google Sheets已分享给服务账号邮箱
- 检查凭证文件路径是否正确
- 确保网络连接正常

### 问题4：WhatsApp添加失败

**解决方法**：
- 当前版本提供模拟实现
- 需要修改 `add_to_whatsapp` 方法，实现实际添加功能
- 参考 README_whatsapp.md 中的自定义开发部分

## 7. 功能扩展

如果您需要实现实际的WhatsApp联系人添加功能，可以修改 `add_to_whatsapp` 方法：

1. 使用pywhatkit库：
   ```python
   def add_to_whatsapp(self, contacts):
       import pywhatkit
       for name, phone in contacts:
           try:
               pywhatkit.sendwhatmsg_instantly(phone, "", 15, True, 2)
               print(f"✓ 成功添加: {name} - {phone}")
               time.sleep(5)
           except Exception as e:
               print(f"✗ 添加失败: {name} - {phone} - {str(e)}")
   ```

2. 使用系统API添加联系人：
   ```python
   def add_to_whatsapp(self, contacts):
       import subprocess
       for name, phone in contacts:
           try:
               if sys.platform == 'win32':
                   # Windows系统
                   cmd = f'powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $contact = New-Object System.Windows.Forms.Application+Contact; $contact.Name = \"{name}\"; $contact.PhoneNumbers.Add(\"{phone}\"); [System.Windows.Forms.Application]::AddContact($contact)"'
               subprocess.run(cmd, shell=True, check=True)
               print(f"✓ 成功添加: {name} - {phone}")
               time.sleep(1)
           except Exception as e:
               print(f"✗ 添加失败: {name} - {phone} - {str(e)}")
   ```

## 8. 注意事项

1. 使用本工具时，请遵守WhatsApp的服务条款
2. 大规模批量添加可能会被WhatsApp检测到，建议适度使用
3. 定期备份配置文件和数据
4. 确保Google Sheets凭证文件的安全性

## 9. 联系信息

如果您在使用过程中遇到问题，可以参考README_whatsapp.md文档，或根据需要修改代码实现更多功能。