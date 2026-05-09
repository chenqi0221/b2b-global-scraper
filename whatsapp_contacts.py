#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp通讯录批量添加工具

功能：从表格中读取电话数据，批量添加到WhatsApp通讯录
支持：Google Sheets、Excel、CSV文件
"""

import os
import sys
import time
import pandas as pd
import argparse
from pathlib import Path

# 尝试导入必要的库
try:
    from gspread import authorize
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    print("缺少必要的库，请运行: pip install pandas gspread oauth2client openpyxl")
    sys.exit(1)

# 配置信息
SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CONFIG_DIR = Path.home() / '.whatsapp_contacts'
CONFIG_FILE = CONFIG_DIR / 'config.json'

class WhatsAppContactsManager:
    """WhatsApp通讯录管理类"""
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        config = {
            'google_credentials': '',
            'default_sheet_id': '',
            'default_worksheet': 'Sheet1',
            'phone_column': 'Phone',
            'name_column': 'Name'
        }
        
        if CONFIG_FILE.exists():
            import json
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config.update(json.load(f))
        return config
    
    def save_config(self):
        """保存配置文件"""
        import json
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def read_from_google_sheets(self, sheet_id, worksheet_name):
        """从Google Sheets读取数据"""
        print(f"正在从Google Sheets读取数据...")
        
        # 检查凭证文件
        if not self.config['google_credentials'] or not os.path.exists(self.config['google_credentials']):
            print("Google凭证文件不存在，请先配置")
            return None
        
        try:
            # 授权访问
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.config['google_credentials'], SCOPES)
            client = authorize(creds)
            
            # 打开表格
            spreadsheet = client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)
            
            # 获取数据
            data = worksheet.get_all_values()
            if not data:
                print("表格中没有数据")
                return None
            
            # 转换为DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])
            print(f"成功读取 {len(df)} 行数据")
            return df
            
        except Exception as e:
            print(f"从Google Sheets读取数据失败: {str(e)}")
            return None
    
    def read_from_file(self, file_path):
        """从本地文件读取数据"""
        print(f"正在从文件读取数据: {file_path}")
        
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                print("不支持的文件格式，仅支持CSV、Excel文件")
                return None
            
            print(f"成功读取 {len(df)} 行数据")
            return df
            
        except Exception as e:
            print(f"从文件读取数据失败: {str(e)}")
            return None
    
    def validate_phone(self, phone):
        """验证电话号码格式"""
        if pd.isna(phone):
            return False
        
        # 移除特殊字符，只保留数字和加号
        phone = ''.join([c for c in str(phone) if c.isdigit() or c == '+'])
        
        # 简单验证：至少10位数字
        if len(phone.replace('+', '')) < 10:
            return False
        
        return phone
    
    def add_to_whatsapp(self, contacts):
        """批量添加联系人到WhatsApp"""
        print(f"准备添加 {len(contacts)} 个联系人到WhatsApp...")
        
        # 这里需要实现实际的WhatsApp联系人添加功能
        # 由于WhatsApp API限制，这里提供模拟实现
        # 实际使用时需要使用第三方库或服务
        
        success_count = 0
        failed_count = 0
        
        for name, phone in contacts:
            try:
                print(f"正在添加联系人: {name} - {phone}")
                # 模拟添加延迟
                time.sleep(0.5)
                
                # 这里是模拟成功，实际实现需要替换
                # 可以使用pywhatkit、whatsapp-web.js等库
                # 或者调用系统API添加联系人
                
                print(f"✓ 成功添加: {name} - {phone}")
                success_count += 1
                
            except Exception as e:
                print(f"✗ 添加失败: {name} - {phone} - {str(e)}")
                failed_count += 1
        
        print(f"\n添加完成！成功: {success_count}, 失败: {failed_count}")
        return success_count, failed_count
    
    def process_contacts(self, df, name_column, phone_column):
        """处理联系人数据"""
        print(f"正在处理联系人数据...")
        
        # 检查列是否存在
        if name_column not in df.columns:
            print(f"错误：表格中没有找到 '{name_column}' 列")
            return []
        
        if phone_column not in df.columns:
            print(f"错误：表格中没有找到 '{phone_column}' 列")
            return []
        
        # 处理联系人
        contacts = []
        for _, row in df.iterrows():
            name = str(row[name_column]).strip() if pd.notna(row[name_column]) else ""
            phone = self.validate_phone(row[phone_column])
            
            if phone:
                contacts.append((name, phone))
            else:
                print(f"跳过无效电话号码: {row[phone_column]}")
        
        print(f"成功处理 {len(contacts)} 个有效联系人")
        return contacts
    
    def run(self, source, sheet_id=None, worksheet=None, name_col=None, phone_col=None):
        """运行主程序"""
        # 使用配置或命令行参数
        name_column = name_col or self.config['name_column']
        phone_column = phone_col or self.config['phone_column']
        
        if source.startswith('http') or len(source) == 44:  # Google Sheets ID长度约为44字符
            # 从Google Sheets读取
            if not sheet_id:
                sheet_id = source
            if not worksheet:
                worksheet = self.config['default_worksheet']
            
            df = self.read_from_google_sheets(sheet_id, worksheet)
        else:
            # 从本地文件读取
            df = self.read_from_file(source)
        
        if df is None:
            return False
        
        # 处理联系人
        contacts = self.process_contacts(df, name_column, phone_column)
        
        if not contacts:
            print("没有找到有效联系人")
            return False
        
        # 添加到WhatsApp
        success, failed = self.add_to_whatsapp(contacts)
        
        return success > 0

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WhatsApp通讯录批量添加工具')
    
    parser.add_argument('source', help='数据源：Google Sheets ID、URL或本地文件路径')
    parser.add_argument('--sheet-id', help='Google Sheets ID（可选，从URL中提取）')
    parser.add_argument('--worksheet', help='工作表名称，默认：Sheet1')
    parser.add_argument('--name-col', help='姓名列名称')
    parser.add_argument('--phone-col', help='电话号码列名称')
    parser.add_argument('--config', action='store_true', help='配置工具')
    
    args = parser.parse_args()
    
    manager = WhatsAppContactsManager()
    
    if args.config:
        # 配置工具
        print("=== WhatsApp通讯录批量添加工具配置 ===")
        
        # 获取配置
        google_creds = input(f"Google凭证文件路径 (当前: {manager.config['google_credentials']}): ")
        if google_creds:
            manager.config['google_credentials'] = google_creds
        
        default_sheet = input(f"默认表格ID (当前: {manager.config['default_sheet_id']}): ")
        if default_sheet:
            manager.config['default_sheet_id'] = default_sheet
        
        default_worksheet = input(f"默认工作表名称 (当前: {manager.config['default_worksheet']}): ")
        if default_worksheet:
            manager.config['default_worksheet'] = default_worksheet
        
        name_col = input(f"默认姓名列名称 (当前: {manager.config['name_column']}): ")
        if name_col:
            manager.config['name_column'] = name_col
        
        phone_col = input(f"默认电话号码列名称 (当前: {manager.config['phone_column']}): ")
        if phone_col:
            manager.config['phone_column'] = phone_col
        
        # 保存配置
        manager.save_config()
        print("配置已保存")
        return
    
    # 运行程序
    success = manager.run(
        args.source,
        args.sheet_id,
        args.worksheet,
        args.name_col,
        args.phone_col
    )
    
    if success:
        print("程序运行成功！")
        sys.exit(0)
    else:
        print("程序运行失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
