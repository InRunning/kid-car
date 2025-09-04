import os
import json
import time
import requests
import yaml
from PIL import Image
from io import BytesIO

# 配置常量
CONFIG_FILE = "local.yaml"
CAR_JSON_FILE = "kid_car_flutter/assets/car.json"
IMAGES_DIR = "kid_car_flutter/assets/images"

# 豆包API配置
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
IMAGE_MODEL = "doubao-seedream-3-0-t2i-250415"

# API密钥和代理配置
API_KEYS = []
CURRENT_API_KEY_INDEX = 0
PROXIES = None

def load_config():
    """加载配置文件"""
    global API_KEYS, PROXIES
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 读取豆包API密钥
    if "Doubao" in config and "ApiKey" in config["Doubao"]:
        API_KEYS.append(config["Doubao"]["ApiKey"])
    
    # 读取代理配置
    if "Proxy" in config:
        PROXIES = {
            "http": config["Proxy"].get("HttpProxy"),
            "https": config["Proxy"].get("HttpsProxy")
        }
        print(f"已配置代理: {PROXIES}")

def get_next_api_key():
    """获取下一个API密钥"""
    global CURRENT_API_KEY_INDEX
    if not API_KEYS:
        raise ValueError("没有可用的API密钥")
    
    api_key = API_KEYS[CURRENT_API_KEY_INDEX]
    CURRENT_API_KEY_INDEX = (CURRENT_API_KEY_INDEX + 1) % len(API_KEYS)
    return api_key

def load_cars_data():
    """加载车辆数据"""
    if not os.path.exists(CAR_JSON_FILE):
        return []
    
    with open('kid_car_flutter/assets/car.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_cars_data(cars_data):
    """保存车辆数据"""
    with open('kid_car_flutter/assets/car.json', 'w', encoding='utf-8') as f:
        json.dump(cars_data, f, ensure_ascii=False, indent=2)

def generate_car_image(car_name, car_type):
    """使用豆包API生成车辆图片"""
    # 创建提示词，明确要求不要出现人物
    if car_type in ['家具', '动物', '天气', '食物', '职业']:
        prompt = f"一个{car_name}，{car_type}，卡通风格，儿童友好，明亮色彩，简单易懂"
    else:
        prompt = f"一辆{car_name}，{car_type}，卡通风格，儿童友好，明亮色彩，简洁背景，不要出现人物，不要出现人，不要有人脸，不要有人形，纯车辆展示"
    
    try:
        # 发送图片生成请求
        api_key = get_next_api_key()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": IMAGE_MODEL,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "watermark": False
        }
        
        response = requests.post(
            f"{BASE_URL}/images/generations",
            headers=headers,
            json=data,
            proxies=PROXIES if PROXIES else None
        )
        
        if response.status_code != 200:
            print(f"✗ 图片生成失败: {car_name}, 状态码: {response.status_code}, 错误: {response.text}")
            return None
        
        result = response.json()
        if "data" not in result or len(result["data"]) == 0:
            print(f"✗ 图片生成失败: {car_name}, 响应格式错误")
            return None
        
        image_url = result["data"][0]["url"]
        
        # 下载生成的图片
        image_response = requests.get(image_url, proxies=PROXIES if PROXIES else None)
        if image_response.status_code != 200:
            print(f"✗ 图片下载失败: {car_name}")
            return None
        
        # 确保images目录存在
        os.makedirs(IMAGES_DIR, exist_ok=True)
        
        # 保存图片
        image_filename = f"{car_name}_{car_type}.jpg"
        image_path = os.path.join(IMAGES_DIR, image_filename)
        
        with open(image_path, 'wb') as f:
            f.write(image_response.content)
        
        print(f"✓ 图片生成成功: {image_path}")
        return image_path
        
    except Exception as e:
        print(f"✗ 图片生成失败: {car_name}, 错误: {str(e)}")
        return None

def main():
    """主函数"""
    # 加载配置
    load_config()
    
    # 加载车辆数据
    cars_data = load_cars_data()
    if not cars_data:
        print("没有找到车辆数据")
        return
    
    print(f"找到 {len(cars_data)} 个车辆数据")
    
    # 统计需要生成图片的车辆数量
    need_generate_count = 0
    for car in cars_data:
        if not car.get("car-image-path"):
            need_generate_count += 1
    
    print(f"其中 {need_generate_count} 个车辆需要生成图片")
    
    # 处理每个车辆
    generated_count = 0
    for car in cars_data:
        # 如果已经有图片路径，跳过
        if car.get("car-image-path"):
            continue
        
        car_name = car["car-name"]
        car_type = car["car-type"]
        
        print(f"正在生成图片: {car_name} ({car_type})")
        
        # 生成图片
        image_path = generate_car_image(car_name, car_type)
        if image_path:
            # 更新车辆数据
            # 将完整路径转换为相对于assets目录的路径
            relative_path = image_path.replace('kid_car_flutter/', '')
            car["car-image-path"] = relative_path
            # 立即保存到JSON文件
            save_cars_data(cars_data)
            generated_count += 1
            print(f"已更新JSON文件: {car_name}")
        
        # 添加延迟，避免请求过于频繁
        time.sleep(2)
    
    print(f"图片生成完成，共生成 {generated_count} 张图片")

if __name__ == "__main__":
    main()