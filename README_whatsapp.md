# WhatsApp通讯录批量添加工具

一个用于从表格中读取电话数据，批量添加到WhatsApp通讯录的Python工具。

## 功能特性

- ✅ 支持从Google Sheets读取数据
- ✅ 支持从本地CSV、Excel文件读取数据
- ✅ 自动验证电话号码格式
- ✅ 批量添加联系人到WhatsApp
- ✅ 支持配置文件保存设置
- ✅ 清晰的日志输出

## 安装步骤

1. 克隆或下载本项目

2. 安装依赖库：
   ```bash
   pip install pandas gspread oauth2client openpyxl
   ```

3. 配置Google Sheets访问权限（如果需要从Google Sheets读取数据）：
   - 前往 [Google Cloud Console](https://console.cloud.google.com/)
   - 创建新项目
   - 启用Google Sheets API和Google Drive API
   - 创建服务账号并下载JSON凭证文件
   - 分享Google Sheets给服务账号的邮箱地址

## 配置说明

运行配置命令：
```bash
python whatsapp_contacts.py --config
```

配置项说明：
- `Google凭证文件路径`: Google Cloud服务账号的JSON凭证文件路径
- `默认表格ID`: 常用的Google Sheets ID
- `默认工作表名称`: 默认读取的工作表，默认为Sheet1
- `默认姓名列名称`: 默认的姓名列，默认为Name
- `默认电话号码列名称`: 默认的电话号码列，默认为Phone

## 使用示例

### 从本地文件读取数据

```bash
# 从CSV文件读取数据
python whatsapp_contacts.py contacts.csv

# 从Excel文件读取数据
python whatsapp_contacts.py contacts.xlsx

# 指定姓名列和电话列
python whatsapp_contacts.py contacts.csv --name-col 姓名 --phone-col 电话
```

### 从Google Sheets读取数据

```bash
# 使用默认配置
python whatsapp_contacts.py YOUR_GOOGLE_SHEETS_ID

# 指定工作表
python whatsapp_contacts.py YOUR_GOOGLE_SHEETS_ID --worksheet Sheet2

# 指定列名称
python whatsapp_contacts.py YOUR_GOOGLE_SHEETS_ID --name-col CustomerName --phone-col PhoneNumber
```

## 注意事项

1. **WhatsApp API限制**：
   - 由于WhatsApp官方API限制，当前版本提供模拟实现
   - 实际使用时需要替换 `add_to_whatsapp` 方法
   - 推荐使用以下方式之一实现实际添加：
     - 使用 `pywhatkit` 库
     - 使用 `whatsapp-web.js` 服务
     - 通过系统API添加联系人

2. **电话号码格式**：
   - 支持国际格式（如：+1234567890）
   - 支持纯数字格式（如：1234567890）
   - 会自动移除特殊字符
   - 至少需要10位数字

3. **Google Sheets访问**：
   - 确保服务账号有表格的读取权限
   - 确保凭证文件路径正确

## 依赖库

- `pandas`: 数据处理
- `gspread`: Google Sheets API访问
- `oauth2client`: Google认证
- `openpyxl`: Excel文件读取

## 代码结构

```
whatsapp_contacts.py
├── WhatsAppContactsManager类
│   ├── load_config() - 加载配置
│   ├── save_config() - 保存配置
│   ├── read_from_google_sheets() - 从Google Sheets读取数据
│   ├── read_from_file() - 从本地文件读取数据
│   ├── validate_phone() - 验证电话号码格式
│   ├── add_to_whatsapp() - 批量添加联系人到WhatsApp
│   ├── process_contacts() - 处理联系人数据
│   └── run() - 运行主程序
└── main() - 命令行入口
```

## 自定义开发

如果需要实现实际的WhatsApp联系人添加功能，可以修改 `add_to_whatsapp` 方法。以下是一些实现建议：

### 使用pywhatkit库

```python
def add_to_whatsapp(self, contacts):
    import pywhatkit
    
    for name, phone in contacts:
        try:
            # 发送一条空白消息来添加联系人
            pywhatkit.sendwhatmsg_instantly(phone, "", 15, True, 2)
            print(f"✓ 成功添加: {name} - {phone}")
            time.sleep(5)  # 避免频率限制
        except Exception as e:
            print(f"✗ 添加失败: {name} - {phone} - {str(e)}")
```

### 使用系统API添加联系人

```python
def add_to_whatsapp(self, contacts):
    import subprocess
    
    for name, phone in contacts:
        try:
            if sys.platform == 'win32':
                # Windows系统
                cmd = f'powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $contact = New-Object System.Windows.Forms.Application+Contact; $contact.Name = \"{name}\"; $contact.PhoneNumbers.Add(\"{phone}\"); [System.Windows.Forms.Application]::AddContact($contact)"'
            elif sys.platform == 'darwin':
                # macOS系统
                cmd = f'osascript -e \"tell application \"Contacts\" to make new person with properties {{first name: \"{name}"}}\" -e \"tell application \"Contacts\" to set value of phone 1 of person 1 to \"{phone}\"\"'
            else:
                # Linux系统
                cmd = f'python3 -c \"import vobject; c = vobject.vCard(); c.add(\'fn\').value = \"{name}\"; tel = c.add(\'tel\'); tel.type_param = \'CELL\'; tel.value = \"{phone}\"; open(\'{name}.vcf\', \'w\').write(c.serialize());\" && gnome-contacts {name}.vcf'
            
            subprocess.run(cmd, shell=True, check=True)
            print(f"✓ 成功添加: {name} - {phone}")
            time.sleep(1)
        except Exception as e:
            print(f"✗ 添加失败: {name} - {phone} - {str(e)}")
```

## 许可证

MIT License

## 免责声明

本工具仅用于学习和研究目的。使用本工具时，请遵守WhatsApp的服务条款和相关法律法规。作者不对使用本工具产生的任何后果负责。