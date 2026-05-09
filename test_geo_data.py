# test_geo_data.py
# 测试地理位置数据结构是否正确

from data import GEOGRAPHICAL_DATA

print("开始测试地理位置数据结构...")

try:
    # 测试大洲访问
    continents = list(GEOGRAPHICAL_DATA.keys())
    print(f"1. 成功获取大洲列表: {continents}")
    
    for continent in continents:
        print(f"\n=== 测试大洲: {continent} ===")
        
        # 测试国家访问
        countries = list(GEOGRAPHICAL_DATA[continent].keys())
        print(f"2. 成功获取国家列表: {countries}")
        
        for country in countries:
            print(f"\n3. 测试国家: {country}")
            
            # 测试国家英文名称访问
            country_en = GEOGRAPHICAL_DATA[continent][country]["en"]
            print(f"   国家英文名称: {country_en}")
            
            # 测试城市访问
            cities = list(GEOGRAPHICAL_DATA[continent][country]["cities"].keys())
            print(f"   城市列表: {cities}")
            
            for city in cities:
                print(f"\n4. 测试城市: {city}")
                
                # 测试区域访问
                districts = GEOGRAPHICAL_DATA[continent][country]["cities"][city]
                print(f"   区域列表: {districts}")
                
                for district in districts:
                    # 测试区域英文和中文名称访问
                    dist_en = district["en"]
                    dist_zh = district["zh"]
                    print(f"   - 区域: {dist_en} ({dist_zh})")
    
    print("\n✅ 所有测试通过！地理位置数据结构正确。")
    
except Exception as e:
    print(f"\n❌ 测试失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()