#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车辆图片生成脚本
读取car.json数据，调用通义千问生成车辆图片
"""

import json
import os
import requests
import time
import yaml
from PIL import Image
from io import BytesIO

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
    # 从配置中获取ModelScope配置
    BASE_URL = 'https://api-inference.modelscope.cn/'
    API_KEYS = config['ModelScope']['ApiKeys']  # 使用所有API key
    IMAGE_MODEL = config['ModelScope']['ImageModel']
    # 获取代理配置
    PROXIES = {}
    if 'Proxy' in config:
        proxy_config = config['Proxy']
        if 'HttpProxy' in proxy_config:
            PROXIES['http'] = proxy_config['HttpProxy']
        if 'HttpsProxy' in proxy_config:
            PROXIES['https'] = proxy_config['HttpsProxy']
else:
    print("使用默认配置")
    BASE_URL = 'https://api-inference.modelscope.cn/'
    API_KEYS = ["ms-149e41d6-fb33-455d-bf45-86e8e97947b1"]  # ModelScope Token
    IMAGE_MODEL = "Qwen/Qwen-Image-Edit"
    PROXIES = {}

# 确保images目录存在
IMAGES_DIR = 'images'
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# 当前使用的API密钥索引
current_key_index = 0

def get_next_api_key():
    """获取下一个API密钥，实现负载均衡"""
    global current_key_index
    key = API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    return key

def create_headers():
    """创建请求头"""
    api_key = get_next_api_key()
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

def generate_car_image(car_info):
    """为单个车辆生成图片"""
    car_name = car_info['car-name']
    car_type = car_info['car-type']
    
    # 构建图片生成提示词
    prompt = f"一辆{car_name}，{car_type}，卡通风格，适合儿童，不要出现人物，背景简洁，色彩鲜艳"
    
    print(f"正在为 {car_name} 生成图片...")
    
    try:
        time.sleep(5)
        # 发送图片生成请求
        response = requests.post(
            f"{BASE_URL}v1/images/generations",
            headers={**create_headers(), "X-ModelScope-Async-Mode": "true"},
            data=json.dumps({
                "model": IMAGE_MODEL,  # 使用配置中的图片生成模型
                "prompt": prompt,
                "n": 1,  # 生成1张图片
                "size": "1024x1024"  # 图片尺寸
            }, ensure_ascii=False).encode('utf-8'),
            proxies=PROXIES if PROXIES else None
        )
        
        response.raise_for_status()
        task_id = response.json()["task_id"]
        
        print(f"任务已提交，任务ID: {task_id}")
        
        # 轮询任务状态
        max_attempts = 60  # 最多等待5分钟
        attempts = 0
        
        while attempts < max_attempts:
            result = requests.get(
                f"{BASE_URL}v1/tasks/{task_id}",
                headers={**create_headers(), "X-ModelScope-Task-Type": "image_generation"},
                proxies=PROXIES if PROXIES else None
            )
            result.raise_for_status()
            data = result.json()
            
            if data["task_status"] == "SUCCEED":
                # 下载生成的图片
                image_url = data["output_images"][0]
                image_response = requests.get(image_url, proxies=PROXIES if PROXIES else None)
                image_response.raise_for_status()
                
                # 保存图片
                image_filename = f"{car_name}_{car_type}.jpg"
                image_path = os.path.join(IMAGES_DIR, image_filename)
                
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                
                print(f"✓ 图片生成成功: {image_path}")
                return image_path
                
            elif data["task_status"] == "FAILED":
                print(f"✗ 图片生成失败: {car_name}")
                return None
            
            # 等待5秒后重试
            time.sleep(5)
            attempts += 1
            
        print(f"✗ 图片生成超时: {car_name}")
        return None
        
    except Exception as e:
        print(f"生成图片时出错: {e}")
        return None

def load_cars_data():
    """加载车辆数据"""
    if os.path.exists('car.json'):
        try:
            with open('car.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取car.json文件失败: {e}")
            return []
    return []

def save_cars_data(cars):
    """保存车辆数据到json文件"""
    try:
        with open('car.json', 'w', encoding='utf-8') as f:
            json.dump(cars, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存car.json文件失败: {e}")
        return False

def main():
    """主函数"""
    print("开始生成车辆图片...")
    
    # 加载车辆数据
    cars = load_cars_data()
    
    if not cars:
        print("错误: 无法加载车辆数据，请先运行car-name.py生成车辆信息")
        return
    
    print(f"共读取到 {len(cars)} 个车辆信息")
    
    # 统计信息
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    # 为每个车辆生成图片
    for i, car in enumerate(cars, 1):
        print(f"\n处理第 {i}/{len(cars)} 个车辆: {car['car-name']}")
        
        # 检查是否已经有图片
        if car.get('car-image-path') and os.path.exists(car['car-image-path']):
            print(f"✓ 图片已存在: {car['car-image-path']}")
            skip_count += 1
            continue
        
        # 生成图片
        image_path = generate_car_image(car)
        
        if image_path:
            # 更新car.json中的图片路径
            car['car-image-path'] = image_path
            success_count += 1
            
            print(f"✓ 成功生成图片: {car['car-name']}")
            
            # 每生成一个就保存一次
            if save_cars_data(cars):
                print(f"  已保存到 car.json")
            else:
                print(f"  保存失败！")
        else:
            fail_count += 1
            print(f"✗ 生成图片失败: {car['car-name']}")
        
        # 添加延迟避免请求过快
        time.sleep(2)
    
    print(f"\n完成！共处理 {len(cars)} 个车辆")
    print(f"成功: {success_count} 个, 失败: {fail_count} 个, 跳过: {skip_count} 个")
    print(f"图片保存在: {IMAGES_DIR}/")

if __name__ == "__main__":
    main()
