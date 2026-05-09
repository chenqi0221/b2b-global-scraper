# test_simple.py
# 简单测试地理位置数据

print("开始简单测试...")

# 只测试基本导入
from data import GEOGRAPHICAL_DATA
print("✅ 成功导入 GEOGRAPHICAL_DATA")

# 测试基本访问
continents = list(GEOGRAPHICAL_DATA.keys())
print(f"✅ 大洲列表: {continents}")

# 测试第一个大洲
first_continent = continents[0]
print(f"✅ 第一个大洲: {first_continent}")

countries = list(GEOGRAPHICAL_DATA[first_continent].keys())
print(f"✅ 国家列表: {countries}")

# 测试第一个国家
first_country = countries[0]
print(f"✅ 第一个国家: {first_country}")

country_data = GEOGRAPHICAL_DATA[first_continent][first_country]
print(f"✅ 国家数据: {country_data}")

# 测试城市访问
cities = list(country_data["cities"].keys())
print(f"✅ 城市列表: {cities}")

# 测试第一个城市
first_city = cities[0]
print(f"✅ 第一个城市: {first_city}")

districts = country_data["cities"][first_city]
print(f"✅ 区域列表: {districts}")

# 测试第一个区域
district = districts[0]
print(f"✅ 第一个区域: {district}")
print(f"✅ 区域英文: {district['en']}")
print(f"✅ 区域中文: {district['zh']}")

print("\n✅ 所有测试通过！")