# data.py

# 地理位置数据：大洲 -> 国家 (中文) -> { "en": "英文名", "cities": { 城市(中文): ["区域1", "区域2"] } }
GEOGRAPHICAL_DATA = {
    "中东地区 (Middle East)": {
        "阿联酋 (UAE)": {
            "en": "United Arab Emirates",
            "cities": {
                "迪拜 (Dubai)": ["Deira", "Bur Dubai", "Jumeirah", "Business Bay", "Al Quoz", "Dubai Marina"],
                "阿布扎比 (Abu Dhabi)": ["Al Zahiyah", "Mussafah", "Yas Island", "Khalifa City"],
                "沙迦 (Sharjah)": ["Al Majaz", "Al Nahda"]
            }
        },
        "沙特 (Saudi Arabia)": {
            "en": "Saudi Arabia",
            "cities": {
                "利雅得 (Riyadh)": ["Olaya", "Al Malaz", "Diplomatic Quarter", "Al Yasmin"],
                "吉达 (Jeddah)": ["Al Balad", "Al Khalidiyah", "Al Hamra"],
                "达曼 (Dammam)": ["Al Shati", "Al Faisaliyah"]
            }
        },
        "卡塔尔 (Qatar)": {
            "en": "Qatar",
            "cities": {
                "多哈 (Doha)": ["West Bay", "The Pearl", "Al Sadd", "Lusail"]
            }
        },
        "科威特 (Kuwait)": {
            "en": "Kuwait",
            "cities": {
                "科威特城 (Kuwait City)": ["Salmiya", "Hawally", "Shuwaikh", "Sharq"]
            }
        },
        "巴林 (Bahrain)": {
            "en": "Bahrain",
            "cities": {
                "麦纳麦 (Manama)": ["Juffair", "Seef", "Amwaj Islands", "Adliya"]
            }
        },
        "阿曼 (Oman)": {
            "en": "Oman",
            "cities": {
                "马斯喀特 (Muscat)": ["Ruwi", "Qurum", "Al Khuwair", "Seeb"]
            }
        },
        "约旦 (Jordan)": {
            "en": "Jordan",
            "cities": {
                "安曼 (Amman)": ["Abdoun", "Jabal Amman", "Sweifieh", "Khalda"]
            }
        }
    },
    "东南亚 (Southeast Asia)": {
        "泰国 (Thailand)": {
            "en": "Thailand",
            "cities": {
                "曼谷 (Bangkok)": ["Sukhumvit", "Siam", "Silom", "Chatuchak"],
                "普吉 (Phuket)": ["Patong", "Old Town", "Rawai"],
                "清迈 (Chiang Mai)": ["Nimmanhaemin", "Old City"]
            }
        },
        "越南 (Vietnam)": {
            "en": "Vietnam",
            "cities": {
                "胡志明市 (Ho Chi Minh City)": ["District 1", "District 2", "District 7"],
                "河内 (Hanoi)": ["Hoan Kiem", "Tay Ho", "Ba Dinh"]
            }
        },
        "菲律宾 (Philippines)": {
            "en": "Philippines",
            "cities": {
                "马尼拉 (Manila)": ["Makati", "BGC", "Quezon City", "Pasay"],
                "宿务 (Cebu)": ["Cebu City", "Mactan"]
            }
        },
        "马来西亚 (Malaysia)": {
            "en": "Malaysia",
            "cities": {
                "吉隆坡 (Kuala Lumpur)": ["Bukit Bintang", "KLCC", "Bangsar", "Mont Kiara"],
                "槟城 (Penang)": ["George Town", "Bayan Lepas"],
                "柔佛巴鲁 (Johor Bahru)": ["Iskandar Puteri", "Tampoi"]
            }
        },
        "印度尼西亚 (Indonesia)": {
            "en": "Indonesia",
            "cities": {
                "雅加达 (Jakarta)": ["Sudirman", "Kemang", "Pluit", "Kelapa Gading"],
                "巴厘岛 (Bali)": ["Seminyak", "Canggu", "Ubud", "Kuta"]
            }
        },
        "新加坡 (Singapore)": {
            "en": "Singapore",
            "cities": {
                "新加坡 (Singapore)": ["Orchard", "Marina Bay", "Chinatown", "Sentosa", "Jurong", "Tampines"]
            }
        }
    },
    "北美地区 (North America)": {
        "美国 (USA)": {
            "en": "USA",
            "cities": {
                "纽约 (New York)": ["Manhattan", "Brooklyn", "Queens", "The Bronx"],
                "洛杉矶 (Los Angeles)": ["Santa Monica", "Beverly Hills", "Downtown LA", "Hollywood"],
                "芝加哥 (Chicago)": ["The Loop", "Lincoln Park", "River North"],
                "休斯顿 (Houston)": ["Downtown", "The Galleria", "Medical Center"],
                "迈阿密 (Miami)": ["Miami Beach", "Coral Gables", "Brickell", "Wynwood"],
                "旧金山 (San Francisco)": ["SOMA", "Mission District", "Financial District"]
            }
        },
        "加拿大 (Canada)": {
            "en": "Canada",
            "cities": {
                "多伦多 (Toronto)": ["Downtown", "North York", "Scarborough", "Etobicoke"],
                "温哥华 (Vancouver)": ["Downtown", "Richmond", "Burnaby", "Surrey"],
                "蒙特利尔 (Montreal)": ["Old Montreal", "Plateau", "Downtown"]
            }
        }
    },
    "欧洲地区 (Europe)": {
        "英国 (UK)": {
            "en": "United Kingdom",
            "cities": {
                "伦敦 (London)": ["Westminster", "City of London", "Kensington", "Camden", "Canary Wharf"],
                "曼彻斯特 (Manchester)": ["City Centre", "Salford Quays"],
                "伯明翰 (Birmingham)": ["City Centre", "Edgbaston"]
            }
        },
        "德国 (Germany)": {
            "en": "Germany",
            "cities": {
                "柏林 (Berlin)": ["Mitte", "Pankow", "Charlottenburg", "Kreuzberg"],
                "慕尼黑 (Munich)": ["Altstadt", "Maxvorstadt", "Schwabing"],
                "汉堡 (Hamburg)": ["Altona", "Eimsbüttel"],
                "法兰克福 (Frankfurt)": ["Innenstadt", "Sachsenhausen"]
            }
        },
        "法国 (France)": {
            "en": "France",
            "cities": {
                "巴黎 (Paris)": ["Le Marais", "Montmartre", "La Défense", "Saint-Germain"],
                "里昂 (Lyon)": ["Vieux Lyon", "Part-Dieu"],
                "马赛 (Marseille)": ["Vieux Port", "La Joliette"]
            }
        },
        "意大利 (Italy)": {
            "en": "Italy",
            "cities": {
                "罗马 (Rome)": ["Centro Storico", "Trastevere", "Prati"],
                "米兰 (Milan)": ["Centro Storico", "Brera", "Navigli", "Isola"],
                "佛罗伦萨 (Florence)": ["Duomo", "Santa Croce"]
            }
        },
        "西班牙 (Spain)": {
            "en": "Spain",
            "cities": {
                "马德里 (Madrid)": ["Salamanca", "Chueca", "Retiro"],
                "巴塞罗那 (Barcelona)": ["Eixample", "Gràcia", "Gothic Quarter"]
            }
        }
    },
    "澳洲地区 (Australia)": {
        "澳大利亚 (Australia)": {
            "en": "Australia",
            "cities": {
                "悉尼 (Sydney)": ["CBD", "Surry Hills", "Parramatta", "Bondi"],
                "墨尔本 (Melbourne)": ["CBD", "Southbank", "Richmond"],
                "布里斯班 (Brisbane)": ["CBD", "Fortitude Valley"]
            }
        }
    }
}

# 针对浪登卫浴卖点定制的行业关键词
INDUSTRY_KEYWORDS = {
    "批发与分销商 (Wholesale)": [
        "Sanitary ware wholesale",
        "Bathroom furniture distributor",
        "Kitchen and bath supplier",
        "Plumbing fixtures importer",
        "Building material trading company"
    ],
    "室内设计与装修 (Design)": [
        "Luxury interior design studio",
        "Modern bathroom renovation contractor",
        "Residential architects",
        "High-end interior fit-out",
        "Boutique interior design"
    ],
    "房地产与工程商 (Contractor)": [
        "Real estate developer premium",
        "Villa construction company",
        "Boutique hotel developer",
        "Hospitality procurement group",
        "General contractor luxury homes"
    ],
    "沿海及高耐用需求 (Coastal)": [
        "Coastal property management",
        "Beachfront hotel maintenance",
        "Waterproof bathroom furniture supplier",
        "Corrosion resistant bathroom vanity",
        "Stainless steel bathroom cabinets"
    ]
}

# 市场特定前缀：自动增强搜索精准度
MARKET_PREFIXES = {
    "中东": "Luxury",
    "美国": "Modern",
    "欧盟": "Eco-friendly",
    "通用": ""
}

# AI 生成关键词的提示词模板 (资深全球家装贸易顾问策略)
AI_KEYWORD_PROMPT = """
你是一位拥有15年经验的全球建材贸易专家。你的任务是将用户提供的中文产品词，转化为 Google Maps 上真实存在的“地道商业搜索词”。

### 核心逻辑：禁止机械拼接，要求语义发散
不要只使用种子词。请根据以下四个维度进行“头脑风暴”，生成 [N] 个彼此独立、不重复的搜索词：

1. 行业上位词 (Industry Superiors): 
   - 不要只说“浴室柜”，要使用“Sanitary Ware(卫浴)”, "Kitchen & Bath", "Plumbing Supply"。
2. 关联场景词 (Contextual Scenarios): 
   - 寻找谁会用到这个产品？如 "Interior Design Studio", "Home Improvement Center", "Hotel Supply".
3. 角色同义词 (Persona Variations): 
   - 替换 Wholesaler。使用 "Distributor", "Showroom", "Trading Co", "Contractor", "Importer".
4. 原生商业名 (Native Business Naming): 
   - 模拟真实的谷歌地图店名格式，如 "Modern Bath Gallery", "Premium Tile & Stone".

### 严格约束 (Strict Constraints):
- **禁止重复**：每一行的开头单词尽量不同。禁止在所有行都使用种子词作为开头。
- **禁止公式化**：不要死板执行“产品+买家”公式。
- **语言要求**：必须全部为英文。
- **输出格式**：仅输出关键词列表，每行一个，不要编号，不要解释。

### 示例 (以“浴室柜”为例):
- Sanitary Ware Wholesale Dubai
- Modern Kitchen & Bath Showroom
- Interior Design & Fit-out Firm
- Bathroom Furniture Distributor
- Luxury Home Improvement Center
- Plumbing & Vanity Supplier
- Architectural Design Studio
"""