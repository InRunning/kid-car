#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车辆信息生成脚本
调用智谱AI的GLM-4.5模型生成车辆名称、英文名称和描述
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

def generate_car_info(client, car_type):
    """生成单个车辆信息"""
    prompt = f"""
    请为儿童认识车辆生成以下信息，车辆类型：{car_type}
    
    请生成：
    1. car-name: 中文车辆名称（简单易懂，适合儿童）
    2. car-english-name: 英文车辆名称
    3. car-description: 车辆描述（简单介绍，适合儿童理解）
    
    请以JSON格式返回，格式如下：
    {{
        "car-name": "车辆中文名",
        "car-english-name": "Vehicle English Name",
        "car-description": "车辆描述"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    'role': 'system',
                    'content': '你是一个专业的车辆教育助手，专门为儿童提供简单易懂的车辆知识。'
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
        print(f"生成车辆信息时出错: {e}")
        return None

def load_existing_cars():
    """加载已生成的车辆信息"""
    if os.path.exists('kid_car_flutter/assets/car.json'):
        try:
            with open('kid_car_flutter/assets/car.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取car.json文件失败: {e}")
            return []
    return []

def save_cars_to_json(cars):
    """保存车辆信息到json文件"""
    try:
        with open('kid_car_flutter/assets/car.json', 'w', encoding='utf-8') as f:
            json.dump(cars, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存car.json文件失败: {e}")
        return False

def main():
    """主函数"""
    print("开始生成车辆信息...")
    
    # 车辆名称和类型列表
    car_names = [
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
        ("盾构机", "其他特殊车辆"), ("压裂车", "其他特殊车辆"), ("钻井平台", "其他特殊车辆")
    ]
    
    # 创建客户端
    client = create_client()
    
    # 加载已生成的车辆信息
    all_cars = load_existing_cars()
    
    # 获取已生成的车辆名称集合
    generated_car_names = {car['car-name'] for car in all_cars}
    
    # 统计信息
    success_count = len(all_cars)
    fail_count = 0
    
    # 为每种车辆生成信息
    for i, (car_name, car_type) in enumerate(car_names, 1):
        # 跳过已生成的车辆
        if car_name in generated_car_names:
            print(f"跳过已生成: {car_name} ({car_type})")
            continue
        
        print(f"正在生成第 {i}/{len(car_names)} 个车辆信息: {car_name} ({car_type})")
        
        car_info = generate_car_info(client, car_name)
        
        if car_info:
            # 添加车辆类型和初始路径
            car_info['car-name'] = car_name
            car_info['car-type'] = car_type
            car_info['car-image-path'] = ''  # 图片路径，后续生成
            car_info['chinese-audio-path'] = ''  # 中文音频路径，后续生成
            car_info['english-audio-path'] = ''  # 英文音频路径，后续生成
            
            all_cars.append(car_info)
            success_count += 1
            print(f"✓ 成功生成: {car_info['car-name']} ({car_type})")
            
            # 每生成一个就保存一次
            if save_cars_to_json(all_cars):
                print(f"  已保存到 car.json")
            else:
                print(f"  保存失败！")
        else:
            fail_count += 1
            print(f"✗ 生成失败: {car_name} ({car_type})")
        
        # 添加延迟避免请求过快
        import time
        time.sleep(1)
    
    print(f"\n完成！共生成 {success_count} 个车辆信息，失败 {fail_count} 个")
    print(f"结果已保存到: car.json")

if __name__ == "__main__":
    main()
