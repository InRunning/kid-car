#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事物信息生成脚本
调用智谱AI的GLM-4.5模型生成事物名称、英文名称、描述和音标
"""

import json
import os
import yaml
from openai import OpenAI

def load_config():
    """从local.yaml加载配置"""
    try:
        with open('local.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return None

# 加载配置
config = load_config()
if config:
    # 使用所有API key
    API_KEYS = config['ModelScope']['ApiKeys']
    MODEL = config['ModelScope']['ChatModel']
else:
    print("使用默认配置")
    API_KEYS = ['ms-149e41d6-fb33-455d-bf45-86e8e97947b1']  # ModelScope Token
    MODEL = 'ZhipuAI/GLM-4.5'

# 当前使用的API密钥索引
current_key_index = 0

def get_next_api_key():
    """获取下一个API密钥，实现负载均衡"""
    global current_key_index
    key = API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    return key

def create_client():
    """创建OpenAI客户端"""
    api_key = get_next_api_key()
    return OpenAI(
        base_url='https://api-inference.modelscope.cn/v1',
        api_key=api_key
    )

def generate_item_info(client, item_type):
    """生成单个事物信息"""
    prompt = f"""
    请为儿童认识事物生成以下信息，事物类型：{item_type}
    
    请生成：
    1. car-name: 中文事物名称（简单易懂，适合儿童）
    2. car-english-name: 英文事物名称
    3. car-description: 事物描述（简单介绍，适合儿童理解，根据类型调整描述内容）
    4. car-english-pronunciation: 英式音标（使用国际音标IPA格式）
    5. car-american-pronunciation: 美式音标（使用国际音标IPA格式）
    
    请以JSON格式返回，格式如下：
    {{
        "car-name": "事物中文名",
        "car-english-name": "Item English Name",
        "car-description": "事物描述",
        "car-english-pronunciation": "/ɪnˈglɪʃ prəˌnʌnsiˈeɪʃən/",
        "car-american-pronunciation": "/ˈæmərɪkən prəˌnʌnsiˈeɪʃən/"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    'role': 'system',
                    'content': '你是一个专业的儿童教育助手，专门为儿童提供简单易懂的各种事物知识，包括车辆、家具、动物、天气、食物和职业等。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            stream=False
        )
        
        # 解析返回的JSON内容
        content = response.choices[0].message.content.strip()
        
        # 尝试提取JSON部分
        if '{' in content and '}' in content:
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            
            try:
                car_info = json.loads(json_str)
                return car_info
            except json.JSONDecodeError:
                print(f"JSON解析失败: {json_str}")
                return None
        else:
            print(f"未找到JSON格式内容: {content}")
            return None
            
    except Exception as e:
        print(f"生成事物信息时出错: {e}")
        return None

def load_existing_items():
    """加载已生成的事物信息"""
    if os.path.exists('kid_car_flutter/assets/car.json'):
        try:
            with open('kid_car_flutter/assets/car.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取car.json文件失败: {e}")
            return []
    return []

def save_items_to_json(items):
    """保存事物信息到json文件"""
    try:
        with open('kid_car_flutter/assets/car.json', 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存car.json文件失败: {e}")
        return False

def main():
    """主函数"""
    print("开始生成事物信息...")
    
    # 事物名称和类型列表
    item_names = [
        # 小型车辆
        ("小汽车", "小型车辆"), ("出租车", "小型车辆"), ("跑车", "小型车辆"), ("越野车", "小型车辆"),
        ("面包车", "小型车辆"), ("皮卡车", "小型车辆"), ("敞篷车", "小型车辆"), ("老爷车", "小型车辆"),
        ("电动汽车", "小型车辆"), ("混合动力车", "小型车辆"), ("三轮车", "小型车辆"), ("摩托车", "小型车辆"),
        ("电动摩托车", "小型车辆"), ("自行车", "小型车辆"), ("电动自行车", "小型车辆"), ("滑板车", "小型车辆"),
        ("平衡车", "小型车辆"), ("卡丁车", "小型车辆"), ("儿童车", "小型车辆"),
        
        # 公共交通
        ("公交车", "公共交通"), ("双层巴士", "公共交通"), ("校车", "公共交通"), ("长途客车", "公共交通"),
        ("地铁", "公共交通"), ("轻轨", "公共交通"), ("有轨电车", "公共交通"), ("火车", "公共交通"),
        ("高铁", "公共交通"), ("动车", "公共交通"), ("磁悬浮列车", "公共交通"), ("单轨列车", "公共交通"), ("缆车", "公共交通"),
        
        # 特种车辆
        ("消防车", "特种车辆"), ("救护车", "特种车辆"), ("警车", "特种车辆"), ("工程车", "特种车辆"),
        ("押运车", "特种车辆"), ("邮政车", "特种车辆"), ("垃圾车", "特种车辆"), ("洒水车", "特种车辆"),
        ("清扫车", "特种车辆"), ("除雪车", "特种车辆"), ("道路救援车", "特种车辆"), ("电视转播车", "特种车辆"), ("移动餐车", "特种车辆"),
        
        # 工程机械
        ("挖掘机", "工程机械"), ("推土机", "工程机械"), ("起重机", "工程机械"), ("装载机", "工程机械"),
        ("压路机", "工程机械"), ("平地机", "工程机械"), ("铲运机", "工程机械"), ("混凝土搅拌车", "工程机械"),
        ("泵车", "工程机械"), ("塔吊", "工程机械"), ("升降机", "工程机械"), ("叉车", "工程机械"), ("吊车", "工程机械"),
        
        # 货运车辆
        ("货车", "货运车辆"), ("大货车", "货运车辆"), ("厢式货车", "货运车辆"), ("冷藏车", "货运车辆"),
        ("油罐车", "货运车辆"), ("自卸车", "货运车辆"), ("半挂车", "货运车辆"), ("全挂车", "货运车辆"),
        ("集装箱卡车", "货运车辆"), ("平板车", "货运车辆"), ("牵引车", "货运车辆"), ("农用车", "货运车辆"), ("三轮货车", "货运车辆"),
        
        # 特殊用途车辆
        ("房车", "特殊用途车辆"), ("露营车", "特殊用途车辆"), ("餐车", "特殊用途车辆"), ("冰淇淋车", "特殊用途车辆"),
        ("移动图书馆", "特殊用途车辆"), ("献血车", "特殊用途车辆"), ("移动医疗车", "特殊用途车辆"), ("观光车", "特殊用途车辆"),
        ("高尔夫球车", "特殊用途车辆"), ("机场摆渡车", "特殊用途车辆"), ("无轨电车", "特殊用途车辆"), ("双层观光巴士", "特殊用途车辆"),
        
        # 紧急救援车辆
        ("消防云梯车", "紧急救援车辆"), ("消防指挥车", "紧急救援车辆"), ("急救车", "紧急救援车辆"), ("救援车", "紧急救援车辆"),
        ("抢险车", "紧急救援车辆"), ("警用摩托车", "紧急救援车辆"), ("防暴车", "紧急救援车辆"), ("装甲车", "紧急救援车辆"),
        ("运兵车", "紧急救援车辆"), ("通信指挥车", "紧急救援车辆"),
        
        # 军用车辆
        ("坦克", "军用车辆"), ("装甲运兵车", "军用车辆"), ("军用吉普", "军用车辆"), ("军用卡车", "军用车辆"),
        ("导弹发射车", "军用车辆"), ("雷达车", "军用车辆"),
        
        # 航空器
        ("飞机", "航空器"), ("直升机", "航空器"), ("战斗机", "航空器"), ("轰炸机", "航空器"), ("运输机", "航空器"),
        ("客机", "航空器"), ("货机", "航空器"), ("水上飞机", "航空器"), ("滑翔机", "航空器"), ("热气球", "航空器"),
        ("飞艇", "航空器"), ("无人机", "航空器"), ("航天飞机", "航空器"),
        
        # 船舶
        ("轮船", "船舶"), ("客轮", "船舶"), ("货轮", "船舶"), ("油轮", "船舶"), ("集装箱船", "船舶"),
        ("渡轮", "船舶"), ("游艇", "船舶"), ("帆船", "船舶"), ("渔船", "船舶"), ("拖船", "船舶"),
        ("驳船", "船舶"), ("气垫船", "船舶"), ("潜水艇", "船舶"), ("破冰船", "船舶"), ("航空母舰", "船舶"),
        ("巡洋舰", "船舶"), ("驱逐舰", "船舶"), ("护卫舰", "船舶"), ("快艇", "船舶"), ("摩托艇", "船舶"),
        ("皮划艇", "船舶"), ("龙舟", "船舶"),
        
        # 农用机械
        ("拖拉机", "农用机械"), ("收割机", "农用机械"), ("播种机", "农用机械"), ("插秧机", "农用机械"),
        ("联合收割机", "农用机械"), ("喷雾器", "农用机械"), ("农用运输车", "农用机械"),
        
        # 其他特殊车辆
        ("月球车", "其他特殊车辆"), ("火星车", "其他特殊车辆"), ("矿用车", "其他特殊车辆"), ("隧道掘进机", "其他特殊车辆"),
        ("盾构机", "其他特殊车辆"), ("压裂车", "其他特殊车辆"), ("钻井平台", "其他特殊车辆"),
        
        # 家具分类
        ("桌子", "家具"), ("椅子", "家具"), ("沙发", "家具"), ("床", "家具"),
        ("书架", "家具"), ("衣柜", "家具"), ("茶几", "家具"), ("电视柜", "家具"),
        ("学习桌", "家具"), ("儿童床", "家具"), ("玩具箱", "家具"), ("鞋柜", "家具"),
        
        # 动物分类
        ("小狗", "动物"), ("小猫", "动物"), ("兔子", "动物"), ("小鸟", "动物"),
        ("金鱼", "动物"), ("仓鼠", "动物"), ("乌龟", "动物"), ("蝴蝶", "动物"),
        ("大象", "动物"), ("长颈鹿", "动物"), ("狮子", "动物"), ("熊猫", "动物"),
        
        # 天气分类
        ("太阳", "天气"), ("云朵", "天气"), ("雨", "天气"), ("雪", "天气"),
        ("彩虹", "天气"), ("风", "天气"), ("雷电", "天气"), ("雾", "天气"),
        ("冰雹", "天气"), ("霜", "天气"), ("露珠", "天气"), ("星空", "天气"),
        
        # 食物分类
        ("苹果", "食物"), ("香蕉", "食物"), ("面包", "食物"), ("牛奶", "食物"),
        ("鸡蛋", "食物"), ("饼干", "食物"), ("果汁", "食物"), ("蔬菜", "食物"),
        ("米饭", "食物"), ("面条", "食物"), ("蛋糕", "食物"), ("冰淇淋", "食物"),
        
        # 职业分类
        ("医生", "职业"), ("护士", "职业"), ("老师", "职业"), ("警察", "职业"),
        ("消防员", "职业"), ("厨师", "职业"), ("司机", "职业"), ("农民", "职业"),
        ("宇航员", "职业"), ("运动员", "职业"), ("画家", "职业"), ("音乐家", "职业")
    ]
    
    # 创建客户端
    client = create_client()
    
    # 加载已生成的事物信息
    all_items = load_existing_items()
    
    # 获取已生成的事物名称集合
    generated_item_names = {item['car-name'] for item in all_items}
    
    # 统计信息
    success_count = len(all_items)
    fail_count = 0
    
    # 为每种事物生成信息
    for i, (item_name, item_type) in enumerate(item_names, 1):
        # 跳过已生成的事物
        if item_name in generated_item_names:
            print(f"跳过已生成: {item_name} ({item_type})")
            continue
        
        print(f"正在生成第 {i}/{len(item_names)} 个事物信息: {item_name} ({item_type})")
        
        item_info = generate_item_info(client, item_name)
        
        if item_info:
            # 添加事物类型和初始路径
            item_info['car-name'] = item_name
            item_info['car-type'] = item_type
            item_info['car-image-path'] = ''  # 图片路径，后续生成
            item_info['chinese-audio-path'] = ''  # 中文音频路径，后续生成
            item_info['english-audio-path'] = ''  # 英文音频路径，后续生成
            
            all_items.append(item_info)
            success_count += 1
            print(f"✓ 成功生成: {item_info['car-name']} ({item_type})")
            
            # 每生成一个就保存一次
            if save_items_to_json(all_items):
                print(f"  已保存到 car.json")
            else:
                print(f"  保存失败！")
        else:
            fail_count += 1
            print(f"✗ 生成失败: {item_name} ({item_type})")
        
        # 添加延迟避免请求过快
        import time
        time.sleep(1)
    
    print(f"\n完成！共生成 {success_count} 个事物信息，失败 {fail_count} 个")
    print(f"结果已保存到: car.json")

if __name__ == "__main__":
    main()
