# data.py

# 地理位置数据：大洲 -> 国家 (中文) -> { "en": "英文名", "cities": { 城市(中文): [{"en": "区域英文名", "zh": "区域中文名"}] } }
GEOGRAPHICAL_DATA = {
    "中东地区 (Middle East)": {
        "阿联酋 (UAE)": {
            "en": "United Arab Emirates",
            "cities": {
                "迪拜 (Dubai)": [
                    {"en": "Deira", "zh": "德拉"}, 
                    {"en": "Bur Dubai", "zh": "布尔迪拜"}, 
                    {"en": "Jumeirah", "zh": "朱美拉"}, 
                    {"en": "Business Bay", "zh": "商业湾"}, 
                    {"en": "Al Quoz", "zh": "阿尔库兹"}, 
                    {"en": "Dubai Marina", "zh": "迪拜码头"}
                ],
                "阿布扎比 (Abu Dhabi)": [
                    {"en": "Al Zahiyah", "zh": "阿尔扎希亚"}, 
                    {"en": "Mussafah", "zh": "穆萨法"}, 
                    {"en": "Yas Island", "zh": "亚斯岛"}, 
                    {"en": "Khalifa City", "zh": "哈利法城"}
                ],
                "沙迦 (Sharjah)": [
                    {"en": "Al Majaz", "zh": "阿尔马贾兹"}, 
                    {"en": "Al Nahda", "zh": "阿尔纳哈达"}
                ]
            }
        },
        "沙特 (Saudi Arabia)": {
            "en": "Saudi Arabia",
            "cities": {
                "利雅得 (Riyadh)": [
                    {"en": "Olaya", "zh": "奥拉亚"}, 
                    {"en": "Al Malaz", "zh": "阿尔马拉兹"}, 
                    {"en": "Diplomatic Quarter", "zh": "外交区"}, 
                    {"en": "Al Yasmin", "zh": "阿尔亚斯明"}
                ],
                "吉达 (Jeddah)": [
                    {"en": "Al Balad", "zh": "阿尔巴拉德"}, 
                    {"en": "Al Khalidiyah", "zh": "阿尔哈利迪亚"}, 
                    {"en": "Al Hamra", "zh": "阿尔哈姆拉"}
                ],
                "达曼 (Dammam)": [
                    {"en": "Al Shati", "zh": "阿尔沙蒂"}, 
                    {"en": "Al Faisaliyah", "zh": "阿尔费萨尔利亚"}
                ]
            }
        },
        "卡塔尔 (Qatar)": {
            "en": "Qatar",
            "cities": {
                "多哈 (Doha)": [
                    {"en": "West Bay", "zh": "西湾"}, 
                    {"en": "The Pearl", "zh": "珍珠岛"}, 
                    {"en": "Al Sadd", "zh": "阿尔萨德"}, 
                    {"en": "Lusail", "zh": "卢塞尔"}
                ]
            }
        },
        "科威特 (Kuwait)": {
            "en": "Kuwait",
            "cities": {
                "科威特城 (Kuwait City)": [
                    {"en": "Salmiya", "zh": "萨尔米亚"}, 
                    {"en": "Hawally", "zh": "哈瓦利"}, 
                    {"en": "Shuwaikh", "zh": "舒韦赫"}, 
                    {"en": "Sharq", "zh": "沙尔克"}
                ]
            }
        },
        "巴林 (Bahrain)": {
            "en": "Bahrain",
            "cities": {
                "麦纳麦 (Manama)": [
                    {"en": "Juffair", "zh": "朱法尔"}, 
                    {"en": "Seef", "zh": "西夫"}, 
                    {"en": "Amwaj Islands", "zh": "阿姆沃杰群岛"}, 
                    {"en": "Adliya", "zh": "阿德利亚"}
                ]
            }
        },
        "阿曼 (Oman)": {
            "en": "Oman",
            "cities": {
                "马斯喀特 (Muscat)": [
                    {"en": "Ruwi", "zh": "鲁维"}, 
                    {"en": "Qurum", "zh": "库鲁姆"}, 
                    {"en": "Al Khuwair", "zh": "阿尔胡瓦尔"}, 
                    {"en": "Seeb", "zh": "西卜"}
                ]
            }
        },
        "约旦 (Jordan)": {
            "en": "Jordan",
            "cities": {
                "安曼 (Amman)": [
                    {"en": "Abdoun", "zh": "阿卜杜恩"}, 
                    {"en": "Jabal Amman", "zh": "安曼山"}, 
                    {"en": "Sweifieh", "zh": "斯韦菲耶"}, 
                    {"en": "Khalda", "zh": "哈尔达"}
                ]
            }
        },
        "以色列 (Israel)": {
            "en": "Israel",
            "cities": {
                "特拉维夫 (Tel Aviv)": [
                    {"en": "Ramat Aviv", "zh": "拉马特阿维夫"}, 
                    {"en": "Florentin", "zh": "弗洛伦丁"}, 
                    {"en": "Neve Tzedek", "zh": "内夫茨德克"}, 
                    {"en": "Jaffa", "zh": "雅法"}
                ],
                "耶路撒冷 (Jerusalem)": [
                    {"en": "Old City", "zh": "老城区"}, 
                    {"en": "Mahane Yehuda", "zh": "马哈尼耶胡达"}, 
                    {"en": "Musrara", "zh": "穆斯拉拉"}
                ],
                "海法 (Haifa)": [
                    {"en": "Hadar", "zh": "哈达尔"}, 
                    {"en": "Carmel", "zh": "卡梅尔"}
                ]
            }
        }
    },
    "东南亚 (Southeast Asia)": {
        "泰国 (Thailand)": {
            "en": "Thailand",
            "cities": {
                "曼谷 (Bangkok)": [
                    {"en": "Sukhumvit", "zh": "素坤逸"}, 
                    {"en": "Siam", "zh": "暹罗"}, 
                    {"en": "Silom", "zh": "是隆"}, 
                    {"en": "Chatuchak", "zh": "恰图恰"}
                ],
                "普吉 (Phuket)": [
                    {"en": "Patong", "zh": "芭东海滩"}, 
                    {"en": "Old Town", "zh": "老城区"}, 
                    {"en": "Rawai", "zh": "拉威"}
                ],
                "清迈 (Chiang Mai)": [
                    {"en": "Nimmanhaemin", "zh": "宁曼路"}, 
                    {"en": "Old City", "zh": "老城区"}
                ]
            }
        },
        "越南 (Vietnam)": {
            "en": "Vietnam",
            "cities": {
                "胡志明市 (Ho Chi Minh City)": [
                    {"en": "District 1", "zh": "第一郡"}, 
                    {"en": "District 2", "zh": "第二郡"}, 
                    {"en": "District 7", "zh": "第七郡"}
                ],
                "河内 (Hanoi)": [
                    {"en": "Hoan Kiem", "zh": "还剑郡"}, 
                    {"en": "Tay Ho", "zh": "西湖郡"}, 
                    {"en": "Ba Dinh", "zh": "巴亭郡"}
                ]
            }
        },
        "菲律宾 (Philippines)": {
            "en": "Philippines",
            "cities": {
                "马尼拉 (Manila)": [
                    {"en": "Makati", "zh": "马卡蒂"}, 
                    {"en": "BGC", "zh": "博尼法西奥环球城"}, 
                    {"en": "Quezon City", "zh": "奎松市"}, 
                    {"en": "Pasay", "zh": "帕赛市"}
                ],
                "宿务 (Cebu)": [
                    {"en": "Cebu City", "zh": "宿务市"}, 
                    {"en": "Mactan", "zh": "麦克坦岛"}
                ]
            }
        },
        "马来西亚 (Malaysia)": {
            "en": "Malaysia",
            "cities": {
                "吉隆坡 (Kuala Lumpur)": [
                    {"en": "Bukit Bintang", "zh": "武吉免登"}, 
                    {"en": "KLCC", "zh": "吉隆坡城中城"}, 
                    {"en": "Bangsar", "zh": "班底谷"}, 
                    {"en": "Mont Kiara", "zh": "满家乐"}
                ],
                "槟城 (Penang)": [
                    {"en": "George Town", "zh": "乔治市"}, 
                    {"en": "Bayan Lepas", "zh": "峇六拜"}
                ],
                "柔佛巴鲁 (Johor Bahru)": [
                    {"en": "Iskandar Puteri", "zh": "依斯干达公主城"}, 
                    {"en": "Tampoi", "zh": "淡杯"}
                ]
            }
        },
        "印度尼西亚 (Indonesia)": {
            "en": "Indonesia",
            "cities": {
                "雅加达 (Jakarta)": [
                    {"en": "Sudirman", "zh": "苏迪尔曼"}, 
                    {"en": "Kemang", "zh": "克芒"}, 
                    {"en": "Pluit", "zh": "普鲁伊特"}, 
                    {"en": "Kelapa Gading", "zh": "椰风新城"}
                ],
                "巴厘岛 (Bali)": [
                    {"en": "Seminyak", "zh": "水明漾"}, 
                    {"en": "Canggu", "zh": "仓古"}, 
                    {"en": "Ubud", "zh": "乌布"}, 
                    {"en": "Kuta", "zh": "库塔"}
                ]
            }
        },
        "新加坡 (Singapore)": {
            "en": "Singapore",
            "cities": {
                "新加坡 (Singapore)": [
                    {"en": "Orchard", "zh": "乌节路"}, 
                    {"en": "Marina Bay", "zh": "滨海湾"}, 
                    {"en": "Chinatown", "zh": "牛车水"}, 
                    {"en": "Sentosa", "zh": "圣淘沙"}, 
                    {"en": "Jurong", "zh": "裕廊"}, 
                    {"en": "Tampines", "zh": "淡滨尼"}
                ]
            }
        }
    },
    "北美地区 (North America)": {
        "美国 (USA)": {
            "en": "USA",
            "cities": {
                "纽约 (New York)": [
                    {"en": "Manhattan", "zh": "曼哈顿"}, 
                    {"en": "Brooklyn", "zh": "布鲁克林"}, 
                    {"en": "Queens", "zh": "皇后区"}, 
                    {"en": "The Bronx", "zh": "布朗克斯"}
                ],
                "洛杉矶 (Los Angeles)": [
                    {"en": "Santa Monica", "zh": "圣莫尼卡"}, 
                    {"en": "Beverly Hills", "zh": "比佛利山庄"}, 
                    {"en": "Downtown LA", "zh": "洛杉矶市中心"}, 
                    {"en": "Hollywood", "zh": "好莱坞"}
                ],
                "芝加哥 (Chicago)": [
                    {"en": "The Loop", "zh": "卢普区"}, 
                    {"en": "Lincoln Park", "zh": "林肯公园"}, 
                    {"en": "River North", "zh": "河北区"}
                ],
                "休斯顿 (Houston)": [
                    {"en": "Downtown", "zh": "市中心"}, 
                    {"en": "The Galleria", "zh": "盖勒里亚"}, 
                    {"en": "Medical Center", "zh": "医疗中心"}
                ],
                "迈阿密 (Miami)": [
                    {"en": "Miami Beach", "zh": "迈阿密海滩"}, 
                    {"en": "Coral Gables", "zh": "科勒尔盖布尔斯"}, 
                    {"en": "Brickell", "zh": "布里克尔"}, 
                    {"en": "Wynwood", "zh": "温伍德"}
                ],
                "旧金山 (San Francisco)": [
                    {"en": "SOMA", "zh": "苏玛区"}, 
                    {"en": "Mission District", "zh": "教会区"}, 
                    {"en": "Financial District", "zh": "金融区"}
                ]
            }
        },
        "加拿大 (Canada)": {
            "en": "Canada",
            "cities": {
                "多伦多 (Toronto)": [
                    {"en": "Downtown", "zh": "市中心"}, 
                    {"en": "North York", "zh": "北约克"}, 
                    {"en": "Scarborough", "zh": "士嘉堡"}, 
                    {"en": "Etobicoke", "zh": "怡陶碧谷"}
                ],
                "温哥华 (Vancouver)": [
                    {"en": "Downtown", "zh": "市中心"}, 
                    {"en": "Richmond", "zh": "列治文"}, 
                    {"en": "Burnaby", "zh": "本拿比"}, 
                    {"en": "Surrey", "zh": "素里"}
                ],
                "蒙特利尔 (Montreal)": [
                    {"en": "Old Montreal", "zh": "蒙特利尔老城"}, 
                    {"en": "Plateau", "zh": "高原区"}, 
                    {"en": "Downtown", "zh": "市中心"}
                ]
            }
        }
    },
    "欧洲地区 (Europe)": {
        "英国 (UK)": {
            "en": "United Kingdom",
            "cities": {
                "伦敦 (London)": [
                    {"en": "Westminster", "zh": "威斯敏斯特"}, 
                    {"en": "City of London", "zh": "伦敦市"}, 
                    {"en": "Kensington", "zh": "肯辛顿"}, 
                    {"en": "Camden", "zh": "卡姆登"}, 
                    {"en": "Canary Wharf", "zh": "金丝雀码头"}
                ],
                "曼彻斯特 (Manchester)": [
                    {"en": "City Centre", "zh": "市中心"}, 
                    {"en": "Salford Quays", "zh": "索尔福德码头"}
                ],
                "伯明翰 (Birmingham)": [
                    {"en": "City Centre", "zh": "市中心"}, 
                    {"en": "Edgbaston", "zh": "埃德巴斯顿"}
                ]
            }
        },
        "德国 (Germany)": {
            "en": "Germany",
            "cities": {
                "柏林 (Berlin)": [
                    {"en": "Mitte", "zh": "米特区"}, 
                    {"en": "Pankow", "zh": "潘科区"}, 
                    {"en": "Charlottenburg", "zh": "夏洛滕堡"}, 
                    {"en": "Kreuzberg", "zh": "克罗伊茨贝格"}
                ],
                "慕尼黑 (Munich)": [
                    {"en": "Altstadt", "zh": "老城区"}, 
                    {"en": "Maxvorstadt", "zh": "马克斯沃思塔特"}, 
                    {"en": "Schwabing", "zh": "施瓦宾"}
                ],
                "汉堡 (Hamburg)": [
                    {"en": "Altona", "zh": "阿尔托纳"}, 
                    {"en": "Eimsbüttel", "zh": "艾姆斯比特尔"}
                ],
                "法兰克福 (Frankfurt)": [
                    {"en": "Innenstadt", "zh": "内城"}, 
                    {"en": "Sachsenhausen", "zh": "萨克森豪森"}
                ]
            }
        },
        "法国 (France)": {
            "en": "France",
            "cities": {
                "巴黎 (Paris)": [
                    {"en": "Le Marais", "zh": "玛莱区"}, 
                    {"en": "Montmartre", "zh": "蒙马特"}, 
                    {"en": "La Défense", "zh": "拉德芳斯"}, 
                    {"en": "Saint-Germain", "zh": "圣日耳曼"}
                ],
                "里昂 (Lyon)": [
                    {"en": "Vieux Lyon", "zh": "里昂老城"}, 
                    {"en": "Part-Dieu", "zh": "帕迪厄"}
                ],
                "马赛 (Marseille)": [
                    {"en": "Vieux Port", "zh": "老港"}, 
                    {"en": "La Joliette", "zh": "拉乔利埃特"}
                ]
            }
        },
        "意大利 (Italy)": {
            "en": "Italy",
            "cities": {
                "罗马 (Rome)": [
                    {"en": "Centro Storico", "zh": "历史中心"}, 
                    {"en": "Trastevere", "zh": "特拉斯特维莱"}, 
                    {"en": "Prati", "zh": "普拉蒂"}
                ],
                "米兰 (Milan)": [
                    {"en": "Centro Storico", "zh": "历史中心"}, 
                    {"en": "Brera", "zh": "布雷拉"}, 
                    {"en": "Navigli", "zh": "纳维利"}, 
                    {"en": "Isola", "zh": "伊索拉"}
                ],
                "佛罗伦萨 (Florence)": [
                    {"en": "Duomo", "zh": "大教堂区"}, 
                    {"en": "Santa Croce", "zh": "圣十字区"}
                ]
            }
        },
        "西班牙 (Spain)": {
            "en": "Spain",
            "cities": {
                "马德里 (Madrid)": [
                    {"en": "Salamanca", "zh": "萨拉曼卡"}, 
                    {"en": "Chueca", "zh": "楚埃卡"}, 
                    {"en": "Retiro", "zh": "丽池"}
                ],
                "巴塞罗那 (Barcelona)": [
                    {"en": "Eixample", "zh": "扩展区"}, 
                    {"en": "Gràcia", "zh": "格拉西亚"}, 
                    {"en": "Gothic Quarter", "zh": "哥特区"}
                ]
            }
        },
        "荷兰 (Netherlands)": {
            "en": "Netherlands",
            "cities": {
                "阿姆斯特丹 (Amsterdam)": [
                    {"en": "Dam Square", "zh": "水坝广场"}, 
                    {"en": "Jordaan", "zh": "约旦区"}, 
                    {"en": "De Pijp", "zh": "皮耶普区"}, 
                    {"en": "Oud-West", "zh": "旧西区"}
                ],
                "鹿特丹 (Rotterdam)": [
                    {"en": "Centrum", "zh": "市中心"}, 
                    {"en": "Kralingen-Crooswijk", "zh": "克拉灵根-克罗斯维克"}
                ]
            }
        },
        "瑞士 (Switzerland)": {
            "en": "Switzerland",
            "cities": {
                "苏黎世 (Zurich)": [
                    {"en": "Altstadt", "zh": "老城区"}, 
                    {"en": "Wipkingen", "zh": "维普金根"}, 
                    {"en": "Enge", "zh": "恩格"}
                ],
                "日内瓦 (Geneva)": [
                    {"en": "Old Town", "zh": "老城区"}, 
                    {"en": "Paquis", "zh": "帕基斯"}
                ]
            }
        }
    },
    "澳洲地区 (Australia)": {
        "澳大利亚 (Australia)": {
            "en": "Australia",
            "cities": {
                "悉尼 (Sydney)": [
                    {"en": "CBD", "zh": "中央商务区"}, 
                    {"en": "Surry Hills", "zh": "萨里山"}, 
                    {"en": "Parramatta", "zh": "帕拉马塔"}, 
                    {"en": "Bondi", "zh": "邦迪"}
                ],
                "墨尔本 (Melbourne)": [
                    {"en": "CBD", "zh": "中央商务区"}, 
                    {"en": "Southbank", "zh": "南岸"}, 
                    {"en": "Richmond", "zh": "里士满"}
                ],
                "布里斯班 (Brisbane)": [
                    {"en": "CBD", "zh": "中央商务区"}, 
                    {"en": "Fortitude Valley", "zh": "毅力谷"}
                ]
            }
        },
        "新西兰 (New Zealand)": {
            "en": "New Zealand",
            "cities": {
                "奥克兰 (Auckland)": [
                    {"en": "CBD", "zh": "中央商务区"}, 
                    {"en": "Parnell", "zh": "帕内尔"}, 
                    {"en": "Devonport", "zh": "德文波特"}
                ],
                "惠灵顿 (Wellington)": [
                    {"en": "CBD", "zh": "中央商务区"}, 
                    {"en": "Te Aro", "zh": "蒂阿罗"}
                ]
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
你是一位拥有15年经验的全球建材贸易专家。你的任务是将用户提供的中文产品词，转化为 Google Maps 上真实存在的“地道商业搜索词”，并提供中文翻译。

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
- **语言要求**：输出英文关键词和对应的中文翻译。
- **输出格式**：格式为 '英文关键词: 中文翻译'，每行一个，不要编号，不要解释。

### 示例 (以“浴室柜”为例):
- Sanitary Ware Wholesale Dubai: 迪拜卫浴批发
- Modern Kitchen & Bath Showroom: 现代厨卫展厅
- Interior Design & Fit-out Firm: 室内设计与装修公司
- Bathroom Furniture Distributor: 浴室家具分销商
- Luxury Home Improvement Center: 豪华家居建材中心
- Plumbing & Vanity Supplier: 管道与梳妆台供应商
- Architectural Design Studio: 建筑设计工作室
"""