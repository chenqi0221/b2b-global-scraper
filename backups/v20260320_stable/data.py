# data.py

# 地理位置数据：国家 (中文) -> { "en": "英文名", "cities": { 城市(中文): ["区域1", "区域2"] } }
GEOGRAPHICAL_DATA = {
    # --- 中东地区 ---
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
    },
    
    # --- 北美地区 ---
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
    },
    
    # --- 欧洲地区 ---
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
    },
    
    # --- 澳洲地区 ---
    "澳大利亚 (Australia)": {
        "en": "Australia",
        "cities": {
            "悉尼 (Sydney)": ["CBD", "Surry Hills", "Parramatta", "Bondi"],
            "墨尔本 (Melbourne)": ["CBD", "Southbank", "Richmond"],
            "布里斯班 (Brisbane)": ["CBD", "Fortitude Valley"]
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