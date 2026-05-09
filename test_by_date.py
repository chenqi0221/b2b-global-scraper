import asyncio
import pandas as pd
from google_sheets_service import upload_to_google_sheets

# 创建测试数据
df1 = pd.DataFrame({
    'Name': ['Test 1', 'Test 2'],
    'Phone': ['1234567890', '0987654321'],
    'Address': ['Address 1', 'Address 2']
})

df2 = pd.DataFrame({
    'Name': ['Test 3', 'Test 4'],
    'Phone': ['1111111111', '2222222222'],
    'Address': ['Address 3', 'Address 4']
})

# 模拟GUI回调函数
def update_status(msg):
    print(msg)

# 测试按日期汇总多工作表功能
async def test_by_date():
    print("测试按日期汇总多工作表功能...")
    
    # 第一次同步
    print("\n=== 第一次同步 ===")
    success1, final_df1 = await upload_to_google_sheets(
        df1, 
        "test_by_date", 
        update_status,
        mode="append",
        by_date=True,
        conflict_resolution="keep_latest"
    )
    print(f"第一次同步成功: {success1}")
    if success1:
        print(f"第一次同步后的数据行数: {len(final_df1)}")
    
    # 第二次同步（同一天）
    print("\n=== 第二次同步（同一天） ===")
    success2, final_df2 = await upload_to_google_sheets(
        df2, 
        "test_by_date", 
        update_status,
        mode="append",
        by_date=True,
        conflict_resolution="keep_latest"
    )
    print(f"第二次同步成功: {success2}")
    if success2:
        print(f"第二次同步后的数据行数: {len(final_df2)}")

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_by_date())