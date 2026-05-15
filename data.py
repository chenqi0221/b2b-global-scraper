AI_KEYWORD_PROMPT = ""

GEOGRAPHICAL_DATA = {
    "亚洲": {
        "中国": {
            "en": "China",
            "cities": {
                "北京 (Beijing)": ["所有", "朝阳区", "海淀区", "丰台区", "通州区", "大兴区"],
                "上海 (Shanghai)": ["所有", "浦东新区", "黄浦区", "徐汇区", "静安区", "闵行区"],
                "深圳 (Shenzhen)": ["所有", "南山区", "福田区", "罗湖区", "宝安区", "龙华区"],
                "广州 (Guangzhou)": ["所有", "天河区", "越秀区", "白云区", "番禺区", "海珠区"],
                "杭州 (Hangzhou)": ["所有", "西湖区", "滨江区", "余杭区", "萧山区"],
                "成都 (Chengdu)": ["所有", "高新区", "武侯区", "锦江区"],
                "武汉 (Wuhan)": ["所有", "洪山区", "江汉区", "武昌区"],
                "南京 (Nanjing)": ["所有", "鼓楼区", "江宁区", "建邺区"],
                "重庆 (Chongqing)": ["所有", "渝中区", "江北区", "渝北区"],
                "天津 (Tianjin)": ["所有", "和平区", "滨海新区", "河西区"],
                "苏州 (Suzhou)": ["所有", "工业园区", "姑苏区", "虎丘区"],
                "东莞 (Dongguan)": ["所有", "南城区", "东城区", "长安镇"],
                "宁波 (Ningbo)": ["所有", "海曙区", "鄞州区", "北仑区"],
                "青岛 (Qingdao)": ["所有", "市南区", "崂山区", "黄岛区"],
                "厦门 (Xiamen)": ["所有", "思明区", "湖里区", "集美区"],
                "西安 (Xian)": ["所有", "雁塔区", "碑林区", "未央区"],
                "长沙 (Changsha)": ["所有", "岳麓区", "芙蓉区", "天心区"],
                "合肥 (Hefei)": ["所有", "蜀山区", "包河区", "庐阳区"],
                "郑州 (Zhengzhou)": ["所有", "金水区", "郑东新区", "二七区"],
                "佛山 (Foshan)": ["所有", "禅城区", "南海区", "顺德区"],
                "福州 (Fuzhou)": ["所有", "鼓楼区", "台江区", "仓山区"],
                "温州 (Wenzhou)": ["所有", "鹿城区", "瓯海区", "龙湾区"],
                "无锡 (Wuxi)": ["所有", "新吴区", "滨湖区", "梁溪区"],
                "大连 (Dalian)": ["所有", "中山区", "西岗区", "沙河口区"],
                "济南 (Jinan)": ["所有", "历下区", "市中区", "槐荫区"],
                "昆明 (Kunming)": ["所有", "五华区", "盘龙区", "官渡区"],
                "哈尔滨 (Harbin)": ["所有", "道里区", "南岗区", "香坊区"],
                "沈阳 (Shenyang)": ["所有", "和平区", "沈河区", "铁西区"],
                "长春 (Changchun)": ["所有", "朝阳区", "南关区", "宽城区"],
                "石家庄 (Shijiazhuang)": ["所有", "长安区", "桥西区", "裕华区"],
                "义乌 (Yiwu)": ["所有"],
                "香港 (Hong Kong)": ["所有", "九龙", "新界", "中环"],
                "台湾 (Taiwan)": ["所有", "台北", "新北", "台中", "高雄"],
                "澳门 (Macau)": ["所有"],
            }
        },
        "日本": {
            "en": "Japan",
            "cities": {
                "东京 (Tokyo)": ["所有", "千代田区", "中央区", "港区", "新宿区", "涩谷区"],
                "大阪 (Osaka)": ["所有", "中央区", "北区", "浪速区", "西区"],
                "名古屋 (Nagoya)": ["所有", "中区", "东区", "千种区"],
                "横滨 (Yokohama)": ["所有", "西区", "中区", "港北区"],
                "神户 (Kobe)": ["所有"],
                "京都 (Kyoto)": ["所有"],
                "福冈 (Fukuoka)": ["所有"],
                "札幌 (Sapporo)": ["所有"],
            }
        },
        "韩国": {
            "en": "South Korea",
            "cities": {
                "首尔 (Seoul)": ["所有", "江南区", "钟路区", "中区", "麻浦区"],
                "釜山 (Busan)": ["所有", "海云台区", "釜山镇区"],
                "仁川 (Incheon)": ["所有"],
                "大邱 (Daegu)": ["所有"],
                "大田 (Daejeon)": ["所有"],
                "光州 (Gwangju)": ["所有"],
            }
        },
        "印度": {
            "en": "India",
            "cities": {
                "新德里 (New Delhi)": ["所有", "德里", "古尔冈", "诺伊达"],
                "孟买 (Mumbai)": ["所有", "南部", "北部", "东部"],
                "班加罗尔 (Bangalore)": ["所有"],
                "金奈 (Chennai)": ["所有"],
                "海得拉巴 (Hyderabad)": ["所有"],
                "加尔各答 (Kolkata)": ["所有"],
                "浦那 (Pune)": ["所有"],
                "艾哈迈达巴德 (Ahmedabad)": ["所有"],
                "斋浦尔 (Jaipur)": ["所有"],
                "勒克瑙 (Lucknow)": ["所有"],
            }
        },
        "越南": {
            "en": "Vietnam",
            "cities": {
                "胡志明市 (Ho Chi Minh City)": ["所有", "第1郡", "第3郡", "平盛郡"],
                "河内 (Hanoi)": ["所有", "还剑郡", "巴亭郡", "纸桥郡"],
                "岘港 (Da Nang)": ["所有"],
                "海防 (Hai Phong)": ["所有"],
                "平阳 (Binh Duong)": ["所有"],
            }
        },
        "泰国": {
            "en": "Thailand",
            "cities": {
                "曼谷 (Bangkok)": ["所有", "素坤逸", "是隆", "拉差达"],
                "清迈 (Chiang Mai)": ["所有"],
                "芭提雅 (Pattaya)": ["所有"],
                "暖武里 (Nonthaburi)": ["所有"],
            }
        },
        "印度尼西亚": {
            "en": "Indonesia",
            "cities": {
                "雅加达 (Jakarta)": ["所有", "南区", "中心区", "西区"],
                "泗水 (Surabaya)": ["所有"],
                "万隆 (Bandung)": ["所有"],
                "棉兰 (Medan)": ["所有"],
                "日惹 (Yogyakarta)": ["所有"],
            }
        },
        "马来西亚": {
            "en": "Malaysia",
            "cities": {
                "吉隆坡 (Kuala Lumpur)": ["所有"],
                "槟城 (Penang)": ["所有"],
                "柔佛巴鲁 (Johor Bahru)": ["所有"],
                "莎阿南 (Shah Alam)": ["所有"],
            }
        },
        "新加坡": {
            "en": "Singapore",
            "cities": {
                "新加坡市 (Singapore City)": ["所有", "市中心", "裕廊", "樟宜", "乌节路"],
            }
        },
        "菲律宾": {
            "en": "Philippines",
            "cities": {
                "马尼拉 (Manila)": ["所有", "马卡蒂", "奎松市", "帕西格", "塔吉格"],
                "宿务 (Cebu)": ["所有"],
                "达沃 (Davao)": ["所有"],
            }
        },
        "巴基斯坦": {
            "en": "Pakistan",
            "cities": {
                "卡拉奇 (Karachi)": ["所有"],
                "拉合尔 (Lahore)": ["所有"],
                "伊斯兰堡 (Islamabad)": ["所有"],
                "费萨拉巴德 (Faisalabad)": ["所有"],
            }
        },
        "孟加拉国": {
            "en": "Bangladesh",
            "cities": {
                "达卡 (Dhaka)": ["所有"],
                "吉大港 (Chittagong)": ["所有"],
            }
        },
        "斯里兰卡": {
            "en": "Sri Lanka",
            "cities": {
                "科伦坡 (Colombo)": ["所有"],
            }
        },
        "缅甸": {
            "en": "Myanmar",
            "cities": {
                "仰光 (Yangon)": ["所有"],
                "曼德勒 (Mandalay)": ["所有"],
            }
        },
        "柬埔寨": {
            "en": "Cambodia",
            "cities": {
                "金边 (Phnom Penh)": ["所有"],
            }
        },
        "老挝": {
            "en": "Laos",
            "cities": {
                "万象 (Vientiane)": ["所有"],
            }
        },
        "尼泊尔": {
            "en": "Nepal",
            "cities": {
                "加德满都 (Kathmandu)": ["所有"],
            }
        },
        "蒙古": {
            "en": "Mongolia",
            "cities": {
                "乌兰巴托 (Ulaanbaatar)": ["所有"],
            }
        },
        "哈萨克斯坦": {
            "en": "Kazakhstan",
            "cities": {
                "阿拉木图 (Almaty)": ["所有"],
                "努尔苏丹 (Nur-Sultan)": ["所有"],
            }
        },
        "乌兹别克斯坦": {
            "en": "Uzbekistan",
            "cities": {
                "塔什干 (Tashkent)": ["所有"],
            }
        },
        "阿联酋": {
            "en": "United Arab Emirates",
            "cities": {
                "迪拜 (Dubai)": ["所有", "迪拜市中心", "迪拜码头", "杰贝阿里", "商业湾"],
                "阿布扎比 (Abu Dhabi)": ["所有"],
                "沙迦 (Sharjah)": ["所有"],
            }
        },
        "沙特阿拉伯": {
            "en": "Saudi Arabia",
            "cities": {
                "利雅得 (Riyadh)": ["所有"],
                "吉达 (Jeddah)": ["所有"],
                "达曼 (Dammam)": ["所有"],
                "麦加 (Mecca)": ["所有"],
            }
        },
        "卡塔尔": {
            "en": "Qatar",
            "cities": {
                "多哈 (Doha)": ["所有"],
            }
        },
        "科威特": {
            "en": "Kuwait",
            "cities": {
                "科威特城 (Kuwait City)": ["所有"],
            }
        },
        "阿曼": {
            "en": "Oman",
            "cities": {
                "马斯喀特 (Muscat)": ["所有"],
            }
        },
        "巴林": {
            "en": "Bahrain",
            "cities": {
                "麦纳麦 (Manama)": ["所有"],
            }
        },
        "以色列": {
            "en": "Israel",
            "cities": {
                "特拉维夫 (Tel Aviv)": ["所有"],
                "耶路撒冷 (Jerusalem)": ["所有"],
                "海法 (Haifa)": ["所有"],
            }
        },
        "土耳其": {
            "en": "Turkey",
            "cities": {
                "伊斯坦布尔 (Istanbul)": ["所有", "欧洲区", "亚洲区"],
                "安卡拉 (Ankara)": ["所有"],
                "伊兹密尔 (Izmir)": ["所有"],
                "布尔萨 (Bursa)": ["所有"],
            }
        },
        "约旦": {
            "en": "Jordan",
            "cities": {
                "安曼 (Amman)": ["所有"],
            }
        },
        "黎巴嫩": {
            "en": "Lebanon",
            "cities": {
                "贝鲁特 (Beirut)": ["所有"],
            }
        },
        "伊朗": {
            "en": "Iran",
            "cities": {
                "德黑兰 (Tehran)": ["所有"],
                "伊斯法罕 (Isfahan)": ["所有"],
            }
        },
        "伊拉克": {
            "en": "Iraq",
            "cities": {
                "巴格达 (Baghdad)": ["所有"],
            }
        },
        "阿塞拜疆": {
            "en": "Azerbaijan",
            "cities": {
                "巴库 (Baku)": ["所有"],
            }
        },
        "格鲁吉亚": {
            "en": "Georgia",
            "cities": {
                "第比利斯 (Tbilisi)": ["所有"],
            }
        },
        "亚美尼亚": {
            "en": "Armenia",
            "cities": {
                "埃里温 (Yerevan)": ["所有"],
            }
        },
    },
    "欧洲": {
        "英国": {
            "en": "United Kingdom",
            "cities": {
                "伦敦 (London)": ["所有", "市中心", "金丝雀码头", "克洛伊登"],
                "曼彻斯特 (Manchester)": ["所有"],
                "伯明翰 (Birmingham)": ["所有"],
                "爱丁堡 (Edinburgh)": ["所有"],
                "格拉斯哥 (Glasgow)": ["所有"],
                "利物浦 (Liverpool)": ["所有"],
                "利兹 (Leeds)": ["所有"],
                "布里斯托 (Bristol)": ["所有"],
                "南安普顿 (Southampton)": ["所有"],
            }
        },
        "德国": {
            "en": "Germany",
            "cities": {
                "柏林 (Berlin)": ["所有"],
                "慕尼黑 (Munich)": ["所有"],
                "法兰克福 (Frankfurt)": ["所有"],
                "汉堡 (Hamburg)": ["所有"],
                "斯图加特 (Stuttgart)": ["所有"],
                "杜塞尔多夫 (Dusseldorf)": ["所有"],
                "科隆 (Cologne)": ["所有"],
                "莱比锡 (Leipzig)": ["所有"],
                "德累斯顿 (Dresden)": ["所有"],
                "纽伦堡 (Nuremberg)": ["所有"],
            }
        },
        "法国": {
            "en": "France",
            "cities": {
                "巴黎 (Paris)": ["所有", "市中心", "拉德芳斯"],
                "里昂 (Lyon)": ["所有"],
                "马赛 (Marseille)": ["所有"],
                "图卢兹 (Toulouse)": ["所有"],
                "尼斯 (Nice)": ["所有"],
                "南特 (Nantes)": ["所有"],
                "斯特拉斯堡 (Strasbourg)": ["所有"],
                "波尔多 (Bordeaux)": ["所有"],
                "里尔 (Lille)": ["所有"],
            }
        },
        "意大利": {
            "en": "Italy",
            "cities": {
                "罗马 (Rome)": ["所有"],
                "米兰 (Milan)": ["所有"],
                "那不勒斯 (Naples)": ["所有"],
                "都灵 (Turin)": ["所有"],
                "佛罗伦萨 (Florence)": ["所有"],
                "博洛尼亚 (Bologna)": ["所有"],
                "热那亚 (Genoa)": ["所有"],
                "威尼斯 (Venice)": ["所有"],
            }
        },
        "西班牙": {
            "en": "Spain",
            "cities": {
                "马德里 (Madrid)": ["所有"],
                "巴塞罗那 (Barcelona)": ["所有"],
                "瓦伦西亚 (Valencia)": ["所有"],
                "塞维利亚 (Seville)": ["所有"],
                "毕尔巴鄂 (Bilbao)": ["所有"],
                "萨拉戈萨 (Zaragoza)": ["所有"],
                "马拉加 (Malaga)": ["所有"],
            }
        },
        "荷兰": {
            "en": "Netherlands",
            "cities": {
                "阿姆斯特丹 (Amsterdam)": ["所有"],
                "鹿特丹 (Rotterdam)": ["所有"],
                "海牙 (The Hague)": ["所有"],
                "乌得勒支 (Utrecht)": ["所有"],
                "埃因霍温 (Eindhoven)": ["所有"],
            }
        },
        "比利时": {
            "en": "Belgium",
            "cities": {
                "布鲁塞尔 (Brussels)": ["所有"],
                "安特卫普 (Antwerp)": ["所有"],
                "根特 (Ghent)": ["所有"],
                "列日 (Liege)": ["所有"],
            }
        },
        "瑞士": {
            "en": "Switzerland",
            "cities": {
                "苏黎世 (Zurich)": ["所有"],
                "日内瓦 (Geneva)": ["所有"],
                "巴塞尔 (Basel)": ["所有"],
                "伯尔尼 (Bern)": ["所有"],
            }
        },
        "奥地利": {
            "en": "Austria",
            "cities": {
                "维也纳 (Vienna)": ["所有"],
                "格拉茨 (Graz)": ["所有"],
                "林茨 (Linz)": ["所有"],
                "萨尔茨堡 (Salzburg)": ["所有"],
            }
        },
        "瑞典": {
            "en": "Sweden",
            "cities": {
                "斯德哥尔摩 (Stockholm)": ["所有"],
                "哥德堡 (Gothenburg)": ["所有"],
                "马尔默 (Malmo)": ["所有"],
            }
        },
        "丹麦": {
            "en": "Denmark",
            "cities": {
                "哥本哈根 (Copenhagen)": ["所有"],
                "奥胡斯 (Aarhus)": ["所有"],
                "欧登塞 (Odense)": ["所有"],
            }
        },
        "挪威": {
            "en": "Norway",
            "cities": {
                "奥斯陆 (Oslo)": ["所有"],
                "卑尔根 (Bergen)": ["所有"],
                "斯塔万格 (Stavanger)": ["所有"],
            }
        },
        "芬兰": {
            "en": "Finland",
            "cities": {
                "赫尔辛基 (Helsinki)": ["所有"],
                "坦佩雷 (Tampere)": ["所有"],
            }
        },
        "波兰": {
            "en": "Poland",
            "cities": {
                "华沙 (Warsaw)": ["所有"],
                "克拉科夫 (Krakow)": ["所有"],
                "弗罗茨瓦夫 (Wroclaw)": ["所有"],
                "波兹南 (Poznan)": ["所有"],
                "格但斯克 (Gdansk)": ["所有"],
            }
        },
        "捷克": {
            "en": "Czech Republic",
            "cities": {
                "布拉格 (Prague)": ["所有"],
                "布尔诺 (Brno)": ["所有"],
            }
        },
        "匈牙利": {
            "en": "Hungary",
            "cities": {
                "布达佩斯 (Budapest)": ["所有"],
            }
        },
        "罗马尼亚": {
            "en": "Romania",
            "cities": {
                "布加勒斯特 (Bucharest)": ["所有"],
                "克卢日-纳波卡 (Cluj-Napoca)": ["所有"],
            }
        },
        "保加利亚": {
            "en": "Bulgaria",
            "cities": {
                "索菲亚 (Sofia)": ["所有"],
                "普罗夫迪夫 (Plovdiv)": ["所有"],
            }
        },
        "希腊": {
            "en": "Greece",
            "cities": {
                "雅典 (Athens)": ["所有"],
                "塞萨洛尼基 (Thessaloniki)": ["所有"],
            }
        },
        "葡萄牙": {
            "en": "Portugal",
            "cities": {
                "里斯本 (Lisbon)": ["所有"],
                "波尔图 (Porto)": ["所有"],
                "布拉加 (Braga)": ["所有"],
            }
        },
        "爱尔兰": {
            "en": "Ireland",
            "cities": {
                "都柏林 (Dublin)": ["所有"],
                "科克 (Cork)": ["所有"],
            }
        },
        "俄罗斯": {
            "en": "Russia",
            "cities": {
                "莫斯科 (Moscow)": ["所有"],
                "圣彼得堡 (Saint Petersburg)": ["所有"],
                "叶卡捷琳堡 (Yekaterinburg)": ["所有"],
                "喀山 (Kazan)": ["所有"],
                "新西伯利亚 (Novosibirsk)": ["所有"],
            }
        },
        "乌克兰": {
            "en": "Ukraine",
            "cities": {
                "基辅 (Kyiv)": ["所有"],
                "利沃夫 (Lviv)": ["所有"],
                "敖德萨 (Odessa)": ["所有"],
            }
        },
        "白俄罗斯": {
            "en": "Belarus",
            "cities": {
                "明斯克 (Minsk)": ["所有"],
            }
        },
        "立陶宛": {
            "en": "Lithuania",
            "cities": {
                "维尔纽斯 (Vilnius)": ["所有"],
                "考纳斯 (Kaunas)": ["所有"],
            }
        },
        "拉脱维亚": {
            "en": "Latvia",
            "cities": {
                "里加 (Riga)": ["所有"],
            }
        },
        "爱沙尼亚": {
            "en": "Estonia",
            "cities": {
                "塔林 (Tallinn)": ["所有"],
            }
        },
        "斯洛伐克": {
            "en": "Slovakia",
            "cities": {
                "布拉迪斯拉发 (Bratislava)": ["所有"],
            }
        },
        "斯洛文尼亚": {
            "en": "Slovenia",
            "cities": {
                "卢布尔雅那 (Ljubljana)": ["所有"],
            }
        },
        "克罗地亚": {
            "en": "Croatia",
            "cities": {
                "萨格勒布 (Zagreb)": ["所有"],
            }
        },
        "塞尔维亚": {
            "en": "Serbia",
            "cities": {
                "贝尔格莱德 (Belgrade)": ["所有"],
            }
        },
        "塞浦路斯": {
            "en": "Cyprus",
            "cities": {
                "尼科西亚 (Nicosia)": ["所有"],
                "利马索尔 (Limassol)": ["所有"],
            }
        },
        "马耳他": {
            "en": "Malta",
            "cities": {
                "瓦莱塔 (Valletta)": ["所有"],
            }
        },
        "卢森堡": {
            "en": "Luxembourg",
            "cities": {
                "卢森堡市 (Luxembourg City)": ["所有"],
            }
        },
    },
    "北美洲": {
        "美国": {
            "en": "United States",
            "cities": {
                "纽约 (New York)": ["所有", "曼哈顿", "布鲁克林", "皇后区", "布朗克斯"],
                "洛杉矶 (Los Angeles)": ["所有", "市中心", "好莱坞", "圣莫尼卡", "长滩"],
                "芝加哥 (Chicago)": ["所有"],
                "休斯顿 (Houston)": ["所有"],
                "旧金山 (San Francisco)": ["所有", "市中心", "硅谷"],
                "圣何塞 (San Jose)": ["所有"],
                "西雅图 (Seattle)": ["所有"],
                "波士顿 (Boston)": ["所有"],
                "迈阿密 (Miami)": ["所有", "市中心", "多拉", "海厄利亚"],
                "达拉斯 (Dallas)": ["所有"],
                "亚特兰大 (Atlanta)": ["所有"],
                "费城 (Philadelphia)": ["所有"],
                "华盛顿 (Washington DC)": ["所有"],
                "圣迭戈 (San Diego)": ["所有"],
                "波特兰 (Portland)": ["所有"],
                "丹佛 (Denver)": ["所有"],
                "凤凰城 (Phoenix)": ["所有"],
                "底特律 (Detroit)": ["所有"],
                "明尼阿波利斯 (Minneapolis)": ["所有"],
                "奥斯汀 (Austin)": ["所有"],
                "奥兰多 (Orlando)": ["所有"],
                "匹兹堡 (Pittsburgh)": ["所有"],
                "盐湖城 (Salt Lake City)": ["所有"],
                "坦帕 (Tampa)": ["所有"],
                "夏洛特 (Charlotte)": ["所有"],
                "拉斯维加斯 (Las Vegas)": ["所有"],
            }
        },
        "加拿大": {
            "en": "Canada",
            "cities": {
                "多伦多 (Toronto)": ["所有", "市中心", "密西沙加", "布兰普顿", "万锦"],
                "温哥华 (Vancouver)": ["所有", "本拿比", "列治文", "素里"],
                "蒙特利尔 (Montreal)": ["所有"],
                "卡尔加里 (Calgary)": ["所有"],
                "渥太华 (Ottawa)": ["所有"],
                "埃德蒙顿 (Edmonton)": ["所有"],
                "魁北克市 (Quebec City)": ["所有"],
                "温尼伯 (Winnipeg)": ["所有"],
                "汉密尔顿 (Hamilton)": ["所有"],
                "滑铁卢 (Waterloo)": ["所有"],
            }
        },
        "墨西哥": {
            "en": "Mexico",
            "cities": {
                "墨西哥城 (Mexico City)": ["所有"],
                "瓜达拉哈拉 (Guadalajara)": ["所有"],
                "蒙特雷 (Monterrey)": ["所有"],
                "蒂华纳 (Tijuana)": ["所有"],
            }
        },
        "古巴": {
            "en": "Cuba",
            "cities": {
                "哈瓦那 (Havana)": ["所有"],
            }
        },
        "牙买加": {
            "en": "Jamaica",
            "cities": {
                "金斯敦 (Kingston)": ["所有"],
            }
        },
        "多米尼加": {
            "en": "Dominican Republic",
            "cities": {
                "圣多明各 (Santo Domingo)": ["所有"],
            }
        },
        "危地马拉": {
            "en": "Guatemala",
            "cities": {
                "危地马拉市 (Guatemala City)": ["所有"],
            }
        },
        "巴拿马": {
            "en": "Panama",
            "cities": {
                "巴拿马城 (Panama City)": ["所有"],
            }
        },
        "哥斯达黎加": {
            "en": "Costa Rica",
            "cities": {
                "圣何塞 (San Jose)": ["所有"],
            }
        },
    },
    "南美洲": {
        "巴西": {
            "en": "Brazil",
            "cities": {
                "圣保罗 (Sao Paulo)": ["所有", "市中心", "保利斯塔大道"],
                "里约热内卢 (Rio de Janeiro)": ["所有"],
                "巴西利亚 (Brasilia)": ["所有"],
                "贝洛奥里藏特 (Belo Horizonte)": ["所有"],
                "库里蒂巴 (Curitiba)": ["所有"],
                "阿雷格里港 (Porto Alegre)": ["所有"],
                "福塔莱萨 (Fortaleza)": ["所有"],
                "萨尔瓦多 (Salvador)": ["所有"],
                "累西腓 (Recife)": ["所有"],
            }
        },
        "阿根廷": {
            "en": "Argentina",
            "cities": {
                "布宜诺斯艾利斯 (Buenos Aires)": ["所有"],
                "科尔多瓦 (Cordoba)": ["所有"],
                "罗萨里奥 (Rosario)": ["所有"],
                "门多萨 (Mendoza)": ["所有"],
            }
        },
        "哥伦比亚": {
            "en": "Colombia",
            "cities": {
                "波哥大 (Bogota)": ["所有"],
                "麦德林 (Medellin)": ["所有"],
                "卡利 (Cali)": ["所有"],
            }
        },
        "智利": {
            "en": "Chile",
            "cities": {
                "圣地亚哥 (Santiago)": ["所有"],
                "瓦尔帕莱索 (Valparaiso)": ["所有"],
            }
        },
        "秘鲁": {
            "en": "Peru",
            "cities": {
                "利马 (Lima)": ["所有"],
            }
        },
        "委内瑞拉": {
            "en": "Venezuela",
            "cities": {
                "加拉加斯 (Caracas)": ["所有"],
                "马拉开波 (Maracaibo)": ["所有"],
            }
        },
        "厄瓜多尔": {
            "en": "Ecuador",
            "cities": {
                "基多 (Quito)": ["所有"],
                "瓜亚基尔 (Guayaquil)": ["所有"],
            }
        },
        "乌拉圭": {
            "en": "Uruguay",
            "cities": {
                "蒙得维的亚 (Montevideo)": ["所有"],
            }
        },
        "巴拉圭": {
            "en": "Paraguay",
            "cities": {
                "亚松森 (Asuncion)": ["所有"],
            }
        },
        "玻利维亚": {
            "en": "Bolivia",
            "cities": {
                "拉巴斯 (La Paz)": ["所有"],
                "圣克鲁斯 (Santa Cruz)": ["所有"],
            }
        },
    },
    "非洲": {
        "南非": {
            "en": "South Africa",
            "cities": {
                "约翰内斯堡 (Johannesburg)": ["所有", "桑顿", "中央商务区"],
                "开普敦 (Cape Town)": ["所有"],
                "德班 (Durban)": ["所有"],
                "比勒陀利亚 (Pretoria)": ["所有"],
            }
        },
        "埃及": {
            "en": "Egypt",
            "cities": {
                "开罗 (Cairo)": ["所有", "新开罗", "十月六日城"],
                "亚历山大 (Alexandria)": ["所有"],
            }
        },
        "尼日利亚": {
            "en": "Nigeria",
            "cities": {
                "拉各斯 (Lagos)": ["所有", "维多利亚岛", "伊科伊"],
                "阿布贾 (Abuja)": ["所有"],
                "哈科特港 (Port Harcourt)": ["所有"],
            }
        },
        "肯尼亚": {
            "en": "Kenya",
            "cities": {
                "内罗毕 (Nairobi)": ["所有"],
                "蒙巴萨 (Mombasa)": ["所有"],
            }
        },
        "加纳": {
            "en": "Ghana",
            "cities": {
                "阿克拉 (Accra)": ["所有"],
                "库马西 (Kumasi)": ["所有"],
            }
        },
        "摩洛哥": {
            "en": "Morocco",
            "cities": {
                "卡萨布兰卡 (Casablanca)": ["所有"],
                "拉巴特 (Rabat)": ["所有"],
                "马拉喀什 (Marrakech)": ["所有"],
            }
        },
        "突尼斯": {
            "en": "Tunisia",
            "cities": {
                "突尼斯 (Tunis)": ["所有"],
            }
        },
        "阿尔及利亚": {
            "en": "Algeria",
            "cities": {
                "阿尔及尔 (Algiers)": ["所有"],
            }
        },
        "坦桑尼亚": {
            "en": "Tanzania",
            "cities": {
                "达累斯萨拉姆 (Dar es Salaam)": ["所有"],
            }
        },
        "埃塞俄比亚": {
            "en": "Ethiopia",
            "cities": {
                "亚的斯亚贝巴 (Addis Ababa)": ["所有"],
            }
        },
        "乌干达": {
            "en": "Uganda",
            "cities": {
                "坎帕拉 (Kampala)": ["所有"],
            }
        },
        "安哥拉": {
            "en": "Angola",
            "cities": {
                "罗安达 (Luanda)": ["所有"],
            }
        },
        "科特迪瓦": {
            "en": "Ivory Coast",
            "cities": {
                "阿比让 (Abidjan)": ["所有"],
            }
        },
        "塞内加尔": {
            "en": "Senegal",
            "cities": {
                "达喀尔 (Dakar)": ["所有"],
            }
        },
        "毛里求斯": {
            "en": "Mauritius",
            "cities": {
                "路易港 (Port Louis)": ["所有"],
            }
        },
        "津巴布韦": {
            "en": "Zimbabwe",
            "cities": {
                "哈拉雷 (Harare)": ["所有"],
            }
        },
        "赞比亚": {
            "en": "Zambia",
            "cities": {
                "卢萨卡 (Lusaka)": ["所有"],
            }
        },
        "莫桑比克": {
            "en": "Mozambique",
            "cities": {
                "马普托 (Maputo)": ["所有"],
            }
        },
        "苏丹": {
            "en": "Sudan",
            "cities": {
                "喀土穆 (Khartoum)": ["所有"],
            }
        },
        "利比亚": {
            "en": "Libya",
            "cities": {
                "的黎波里 (Tripoli)": ["所有"],
            }
        },
        "刚果金": {
            "en": "DR Congo",
            "cities": {
                "金沙萨 (Kinshasa)": ["所有"],
            }
        },
        "喀麦隆": {
            "en": "Cameroon",
            "cities": {
                "杜阿拉 (Douala)": ["所有"],
                "雅温得 (Yaounde)": ["所有"],
            }
        },
    },
    "大洋洲": {
        "澳大利亚": {
            "en": "Australia",
            "cities": {
                "悉尼 (Sydney)": ["所有", "市中心", "北悉尼", "帕拉马塔"],
                "墨尔本 (Melbourne)": ["所有", "市中心", "南岸", "码头区"],
                "布里斯班 (Brisbane)": ["所有"],
                "珀斯 (Perth)": ["所有"],
                "阿德莱德 (Adelaide)": ["所有"],
                "黄金海岸 (Gold Coast)": ["所有"],
                "堪培拉 (Canberra)": ["所有"],
                "纽卡斯尔 (Newcastle)": ["所有"],
            }
        },
        "新西兰": {
            "en": "New Zealand",
            "cities": {
                "奥克兰 (Auckland)": ["所有", "市中心", "北岸", "曼努考"],
                "惠灵顿 (Wellington)": ["所有"],
                "基督城 (Christchurch)": ["所有"],
                "汉密尔顿 (Hamilton)": ["所有"],
            }
        },
        "巴布亚新几内亚": {
            "en": "Papua New Guinea",
            "cities": {
                "莫尔兹比港 (Port Moresby)": ["所有"],
            }
        },
        "斐济": {
            "en": "Fiji",
            "cities": {
                "苏瓦 (Suva)": ["所有"],
            }
        },
    },
}

INDUSTRY_KEYWORDS = {
    "电子产品": [
        {"en": "electronics supplier", "zh": "电子产品供应商"},
        {"en": "electronic components manufacturer", "zh": "电子元件制造商"},
        {"en": "consumer electronics wholesale", "zh": "消费电子批发"},
        {"en": "electronic parts distributor", "zh": "电子零件分销商"},
        {"en": "electronics factory", "zh": "电子工厂"},
    ],
    "手机配件": [
        {"en": "phone accessories supplier", "zh": "手机配件供应商"},
        {"en": "mobile phone case manufacturer", "zh": "手机壳制造商"},
        {"en": "phone charger wholesale", "zh": "手机充电器批发"},
        {"en": "screen protector factory", "zh": "屏幕保护膜工厂"},
        {"en": "mobile accessories distributor", "zh": "手机配件分销商"},
    ],
    "电脑及配件": [
        {"en": "computer hardware supplier", "zh": "电脑硬件供应商"},
        {"en": "laptop accessories manufacturer", "zh": "笔记本配件制造商"},
        {"en": "computer parts wholesale", "zh": "电脑配件批发"},
        {"en": "IT hardware distributor", "zh": "IT硬件分销商"},
        {"en": "computer peripheral factory", "zh": "电脑外设工厂"},
    ],
    "LED照明": [
        {"en": "LED lighting supplier", "zh": "LED照明供应商"},
        {"en": "LED light manufacturer", "zh": "LED灯制造商"},
        {"en": "LED lamp wholesale", "zh": "LED灯批发"},
        {"en": "LED strip factory", "zh": "LED灯带工厂"},
        {"en": "lighting fixture distributor", "zh": "灯具分销商"},
    ],
    "太阳能": [
        {"en": "solar panel supplier", "zh": "太阳能板供应商"},
        {"en": "solar energy equipment manufacturer", "zh": "太阳能设备制造商"},
        {"en": "solar inverter wholesale", "zh": "太阳能逆变器批发"},
        {"en": "solar battery factory", "zh": "太阳能电池工厂"},
        {"en": "renewable energy distributor", "zh": "可再生能源分销商"},
    ],
    "家电": [
        {"en": "home appliance supplier", "zh": "家电供应商"},
        {"en": "household appliance manufacturer", "zh": "家用电器制造商"},
        {"en": "kitchen appliance wholesale", "zh": "厨房电器批发"},
        {"en": "small appliance factory", "zh": "小家电工厂"},
        {"en": "electrical appliance distributor", "zh": "电器分销商"},
    ],
    "家具": [
        {"en": "furniture supplier", "zh": "家具供应商"},
        {"en": "furniture manufacturer", "zh": "家具制造商"},
        {"en": "office furniture wholesale", "zh": "办公家具批发"},
        {"en": "home furniture exporter", "zh": "家用家具出口商"},
        {"en": "custom furniture factory", "zh": "定制家具工厂"},
    ],
    "灯具": [
        {"en": "lighting fixture supplier", "zh": "灯具供应商"},
        {"en": "chandelier manufacturer", "zh": "吊灯制造商"},
        {"en": "decorative lighting wholesale", "zh": "装饰灯批发"},
        {"en": "ceiling light factory", "zh": "吸顶灯工厂"},
        {"en": "lamp distributor", "zh": "灯具分销商"},
    ],
    "卫浴": [
        {"en": "bathroom fixture supplier", "zh": "卫浴配件供应商"},
        {"en": "sanitary ware manufacturer", "zh": "卫浴制造商"},
        {"en": "bathroom vanity wholesale", "zh": "浴室柜批发"},
        {"en": "shower enclosure factory", "zh": "淋浴房工厂"},
        {"en": "bathroom accessory distributor", "zh": "卫浴配件分销商"},
    ],
    "建材": [
        {"en": "building material supplier", "zh": "建材供应商"},
        {"en": "construction material manufacturer", "zh": "建筑材料制造商"},
        {"en": "building supply wholesale", "zh": "建材批发"},
        {"en": "hardware material factory", "zh": "五金材料工厂"},
        {"en": "construction material distributor", "zh": "建材分销商"},
    ],
    "五金工具": [
        {"en": "hardware tools supplier", "zh": "五金工具供应商"},
        {"en": "hand tool manufacturer", "zh": "手动工具制造商"},
        {"en": "power tool wholesale", "zh": "电动工具批发"},
        {"en": "hardware factory", "zh": "五金工厂"},
        {"en": "tool distributor", "zh": "工具分销商"},
    ],
    "门窗": [
        {"en": "door window supplier", "zh": "门窗供应商"},
        {"en": "door window manufacturer", "zh": "门窗制造商"},
        {"en": "aluminum window wholesale", "zh": "铝窗批发"},
        {"en": "steel door factory", "zh": "钢门工厂"},
        {"en": "window door distributor", "zh": "门窗分销商"},
    ],
    "石材陶瓷": [
        {"en": "stone tile supplier", "zh": "石材瓷砖供应商"},
        {"en": "ceramic tile manufacturer", "zh": "瓷砖制造商"},
        {"en": "marble wholesale", "zh": "大理石批发"},
        {"en": "granite factory", "zh": "花岗岩工厂"},
        {"en": "porcelain tile distributor", "zh": "瓷砖分销商"},
    ],
    "服装": [
        {"en": "clothing supplier", "zh": "服装供应商"},
        {"en": "garment manufacturer", "zh": "服装制造商"},
        {"en": "apparel wholesale", "zh": "服装批发"},
        {"en": "textile factory", "zh": "纺织工厂"},
        {"en": "fashion clothing distributor", "zh": "时尚服装分销商"},
    ],
    "鞋类": [
        {"en": "footwear supplier", "zh": "鞋类供应商"},
        {"en": "shoe manufacturer", "zh": "鞋制造商"},
        {"en": "sneaker wholesale", "zh": "运动鞋批发"},
        {"en": "shoe factory", "zh": "鞋厂"},
        {"en": "footwear distributor", "zh": "鞋类分销商"},
    ],
    "箱包": [
        {"en": "bag supplier", "zh": "箱包供应商"},
        {"en": "luggage manufacturer", "zh": "行李箱制造商"},
        {"en": "handbag wholesale", "zh": "手提包批发"},
        {"en": "backpack factory", "zh": "背包工厂"},
        {"en": "bag distributor", "zh": "箱包分销商"},
    ],
    "纺织面料": [
        {"en": "fabric supplier", "zh": "面料供应商"},
        {"en": "textile manufacturer", "zh": "纺织品制造商"},
        {"en": "fabric wholesale", "zh": "面料批发"},
        {"en": "textile mill", "zh": "纺织厂"},
        {"en": "textile distributor", "zh": "纺织品分销商"},
    ],
    "珠宝首饰": [
        {"en": "jewelry supplier", "zh": "珠宝供应商"},
        {"en": "jewelry manufacturer", "zh": "珠宝制造商"},
        {"en": "fashion jewelry wholesale", "zh": "时尚珠宝批发"},
        {"en": "silver jewelry factory", "zh": "银饰工厂"},
        {"en": "jewelry distributor", "zh": "珠宝分销商"},
    ],
    "化妆品": [
        {"en": "cosmetics supplier", "zh": "化妆品供应商"},
        {"en": "cosmetics manufacturer", "zh": "化妆品制造商"},
        {"en": "skincare wholesale", "zh": "护肤品批发"},
        {"en": "makeup factory", "zh": "彩妆工厂"},
        {"en": "beauty product distributor", "zh": "美容产品分销商"},
    ],
    "食品饮料": [
        {"en": "food beverage supplier", "zh": "食品饮料供应商"},
        {"en": "food product manufacturer", "zh": "食品制造商"},
        {"en": "beverage wholesale", "zh": "饮料批发"},
        {"en": "snack food factory", "zh": "零食工厂"},
        {"en": "food distributor", "zh": "食品分销商"},
    ],
    "农产品": [
        {"en": "agricultural product supplier", "zh": "农产品供应商"},
        {"en": "farm produce exporter", "zh": "农产品出口商"},
        {"en": "grain wholesale", "zh": "粮食批发"},
        {"en": "fresh produce distributor", "zh": "生鲜分销商"},
        {"en": "agricultural commodity trader", "zh": "农产品贸易商"},
    ],
    "海鲜水产": [
        {"en": "seafood supplier", "zh": "海鲜供应商"},
        {"en": "fishery product exporter", "zh": "水产品出口商"},
        {"en": "frozen seafood wholesale", "zh": "冷冻海鲜批发"},
        {"en": "aquaculture farm", "zh": "水产养殖场"},
        {"en": "seafood distributor", "zh": "海鲜分销商"},
    ],
    "汽车零部件": [
        {"en": "auto parts supplier", "zh": "汽车零部件供应商"},
        {"en": "automotive parts manufacturer", "zh": "汽车零部件制造商"},
        {"en": "car accessories wholesale", "zh": "汽车配件批发"},
        {"en": "auto spare parts factory", "zh": "汽车零配件工厂"},
        {"en": "automotive parts distributor", "zh": "汽车零部件分销商"},
    ],
    "摩托车": [
        {"en": "motorcycle supplier", "zh": "摩托车供应商"},
        {"en": "motorcycle parts manufacturer", "zh": "摩托车配件制造商"},
        {"en": "motorcycle accessory wholesale", "zh": "摩托车配件批发"},
        {"en": "e-bike factory", "zh": "电动自行车工厂"},
        {"en": "motorcycle distributor", "zh": "摩托车分销商"},
    ],
    "机械设备": [
        {"en": "machinery equipment supplier", "zh": "机械设备供应商"},
        {"en": "industrial machinery manufacturer", "zh": "工业机械制造商"},
        {"en": "machine tool wholesale", "zh": "机床批发"},
        {"en": "equipment factory", "zh": "设备工厂"},
        {"en": "industrial equipment distributor", "zh": "工业设备分销商"},
    ],
    "工程机械": [
        {"en": "construction machinery supplier", "zh": "工程机械供应商"},
        {"en": "heavy equipment manufacturer", "zh": "重型设备制造商"},
        {"en": "excavator wholesale", "zh": "挖掘机批发"},
        {"en": "construction equipment dealer", "zh": "工程设备经销商"},
        {"en": "earthmoving machinery distributor", "zh": "土方机械分销商"},
    ],
    "机床": [
        {"en": "CNC machine supplier", "zh": "数控机床供应商"},
        {"en": "machine tool manufacturer", "zh": "机床制造商"},
        {"en": "lathe machine wholesale", "zh": "车床批发"},
        {"en": "milling machine factory", "zh": "铣床工厂"},
        {"en": "precision machinery distributor", "zh": "精密机械分销商"},
    ],
    "包装印刷": [
        {"en": "packaging supplier", "zh": "包装供应商"},
        {"en": "packaging material manufacturer", "zh": "包装材料制造商"},
        {"en": "printing service wholesale", "zh": "印刷服务批发"},
        {"en": "paper packaging factory", "zh": "纸包装工厂"},
        {"en": "packaging distributor", "zh": "包装分销商"},
    ],
    "塑料制品": [
        {"en": "plastic product supplier", "zh": "塑料制品供应商"},
        {"en": "plastic injection molding manufacturer", "zh": "注塑制造商"},
        {"en": "plastic material wholesale", "zh": "塑料材料批发"},
        {"en": "plastic container factory", "zh": "塑料容器工厂"},
        {"en": "plastic goods distributor", "zh": "塑料制品分销商"},
    ],
    "橡胶制品": [
        {"en": "rubber product supplier", "zh": "橡胶制品供应商"},
        {"en": "rubber seal manufacturer", "zh": "橡胶密封件制造商"},
        {"en": "rubber hose wholesale", "zh": "橡胶软管批发"},
        {"en": "rubber gasket factory", "zh": "橡胶垫片工厂"},
        {"en": "rubber parts distributor", "zh": "橡胶零件分销商"},
    ],
    "化工": [
        {"en": "chemical supplier", "zh": "化工供应商"},
        {"en": "chemical manufacturer", "zh": "化工制造商"},
        {"en": "industrial chemical wholesale", "zh": "工业化学品批发"},
        {"en": "chemical raw material factory", "zh": "化工原料工厂"},
        {"en": "chemical distributor", "zh": "化工分销商"},
    ],
    "医疗器械": [
        {"en": "medical device supplier", "zh": "医疗器械供应商"},
        {"en": "medical equipment manufacturer", "zh": "医疗设备制造商"},
        {"en": "medical supply wholesale", "zh": "医疗用品批发"},
        {"en": "surgical instrument factory", "zh": "手术器械工厂"},
        {"en": "medical product distributor", "zh": "医疗产品分销商"},
    ],
    "制药": [
        {"en": "pharmaceutical supplier", "zh": "制药供应商"},
        {"en": "pharmaceutical manufacturer", "zh": "制药制造商"},
        {"en": "medicine wholesale", "zh": "药品批发"},
        {"en": "pharma factory", "zh": "制药工厂"},
        {"en": "drug distributor", "zh": "药品分销商"},
    ],
    "实验室设备": [
        {"en": "laboratory equipment supplier", "zh": "实验室设备供应商"},
        {"en": "lab instrument manufacturer", "zh": "实验室仪器制造商"},
        {"en": "scientific equipment wholesale", "zh": "科学设备批发"},
        {"en": "lab supply distributor", "zh": "实验室用品分销商"},
        {"en": "testing equipment factory", "zh": "检测设备工厂"},
    ],
    "体育用品": [
        {"en": "sports equipment supplier", "zh": "体育用品供应商"},
        {"en": "sporting goods manufacturer", "zh": "体育用品制造商"},
        {"en": "fitness equipment wholesale", "zh": "健身器材批发"},
        {"en": "sportswear factory", "zh": "运动服装工厂"},
        {"en": "sports goods distributor", "zh": "体育用品分销商"},
    ],
    "玩具": [
        {"en": "toy supplier", "zh": "玩具供应商"},
        {"en": "toy manufacturer", "zh": "玩具制造商"},
        {"en": "plastic toy wholesale", "zh": "塑料玩具批发"},
        {"en": "educational toy factory", "zh": "益智玩具工厂"},
        {"en": "toy distributor", "zh": "玩具分销商"},
    ],
    "母婴用品": [
        {"en": "baby product supplier", "zh": "母婴用品供应商"},
        {"en": "maternity product manufacturer", "zh": "孕产用品制造商"},
        {"en": "baby care wholesale", "zh": "婴儿护理批发"},
        {"en": "children product factory", "zh": "儿童用品工厂"},
        {"en": "baby goods distributor", "zh": "母婴用品分销商"},
    ],
    "宠物用品": [
        {"en": "pet supply supplier", "zh": "宠物用品供应商"},
        {"en": "pet product manufacturer", "zh": "宠物用品制造商"},
        {"en": "pet food wholesale", "zh": "宠物食品批发"},
        {"en": "pet accessory factory", "zh": "宠物配件工厂"},
        {"en": "pet goods distributor", "zh": "宠物用品分销商"},
    ],
    "办公用品": [
        {"en": "office supply supplier", "zh": "办公用品供应商"},
        {"en": "stationery manufacturer", "zh": "文具制造商"},
        {"en": "office furniture wholesale", "zh": "办公家具批发"},
        {"en": "office equipment dealer", "zh": "办公设备经销商"},
        {"en": "school supply distributor", "zh": "学校用品分销商"},
    ],
    "安防监控": [
        {"en": "security camera supplier", "zh": "安防摄像头供应商"},
        {"en": "CCTV manufacturer", "zh": "监控制造商"},
        {"en": "surveillance system wholesale", "zh": "监控系统批发"},
        {"en": "security equipment factory", "zh": "安防设备工厂"},
        {"en": "alarm system distributor", "zh": "报警系统分销商"},
    ],
    "物流仓储": [
        {"en": "logistics service provider", "zh": "物流服务提供商"},
        {"en": "warehouse equipment supplier", "zh": "仓储设备供应商"},
        {"en": "freight forwarding company", "zh": "货运代理公司"},
        {"en": "shipping agent", "zh": "船运代理"},
        {"en": "supply chain service provider", "zh": "供应链服务商"},
    ],
    "酒店用品": [
        {"en": "hotel supply supplier", "zh": "酒店用品供应商"},
        {"en": "hotel furniture manufacturer", "zh": "酒店家具制造商"},
        {"en": "hotel linen wholesale", "zh": "酒店布草批发"},
        {"en": "hospitality product factory", "zh": "酒店用品工厂"},
        {"en": "hotel equipment distributor", "zh": "酒店设备分销商"},
    ],
    "礼品促销品": [
        {"en": "promotional gift supplier", "zh": "促销礼品供应商"},
        {"en": "corporate gift manufacturer", "zh": "企业礼品制造商"},
        {"en": "custom gift wholesale", "zh": "定制礼品批发"},
        {"en": "souvenir factory", "zh": "纪念品工厂"},
        {"en": "advertising gift distributor", "zh": "广告礼品分销商"},
    ],
    "眼镜": [
        {"en": "eyewear supplier", "zh": "眼镜供应商"},
        {"en": "optical frame manufacturer", "zh": "眼镜框制造商"},
        {"en": "sunglasses wholesale", "zh": "太阳镜批发"},
        {"en": "reading glasses factory", "zh": "老花镜工厂"},
        {"en": "optical lens distributor", "zh": "光学镜片分销商"},
    ],
    "钟表": [
        {"en": "watch supplier", "zh": "钟表供应商"},
        {"en": "watch manufacturer", "zh": "钟表制造商"},
        {"en": "timepiece wholesale", "zh": "钟表批发"},
        {"en": "clock factory", "zh": "钟表工厂"},
        {"en": "watch distributor", "zh": "钟表分销商"},
    ],
    "乐器": [
        {"en": "musical instrument supplier", "zh": "乐器供应商"},
        {"en": "guitar manufacturer", "zh": "吉他制造商"},
        {"en": "music instrument wholesale", "zh": "乐器批发"},
        {"en": "musical equipment factory", "zh": "乐器设备工厂"},
        {"en": "instrument distributor", "zh": "乐器分销商"},
    ],
    "电动车": [
        {"en": "electric vehicle supplier", "zh": "电动车供应商"},
        {"en": "electric scooter manufacturer", "zh": "电动滑板车制造商"},
        {"en": "e-bike wholesale", "zh": "电动自行车批发"},
        {"en": "electric tricycle factory", "zh": "电动三轮车工厂"},
        {"en": "EV parts distributor", "zh": "电动车零件分销商"},
    ],
    "电缆电线": [
        {"en": "cable wire supplier", "zh": "电缆电线供应商"},
        {"en": "electrical cable manufacturer", "zh": "电缆制造商"},
        {"en": "power cable wholesale", "zh": "电力电缆批发"},
        {"en": "wire harness factory", "zh": "线束工厂"},
        {"en": "electrical wire distributor", "zh": "电线分销商"},
    ],
}
