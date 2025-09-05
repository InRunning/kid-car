#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import yaml
import requests
import random
from pathlib import Path

def load_config():
    """加载配置文件"""
    with open('local.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_car_data():
    """加载汽车数据"""
    with open('car.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_apple_icon():
    """生成苹果图标"""
    # 加载配置
    config = load_config()
    
    # 苹果的描述信息
    apple_description = "苹果是一种常见的水果，通常是红色、绿色或黄色的。它圆圆的，吃起来脆脆甜甜的，很有营养。苹果可以生吃，也可以做成果汁、苹果派等美食。俗话说：'一天一苹果，医生远离我'，说明吃苹果对健康很有好处。"
    
    # 创建输出目录
    output_dir = Path('kid_car_flutter/assets/images')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 输出路径
    output_path = output_dir / '苹果_水果.jpg'
    
    # 随机选择一个API密钥
    api_keys = config['ModelScope']['ApiKeys']
    api_key = random.choice(api_keys)
    
    # API端点 - 使用ModelScope通用推理API
    api_url = "https://api-inference.modelscope.cn/v1/models/AI-ModelScope/stable-diffusion-2-1"
    
    # 请求头 - ModelScope API格式
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    # 构建提示词
    prompt = f"""
    请生成一个可爱的、适合儿童的苹果图标，用于儿童学习应用。
    
    要求：
    - 简洁扁平化设计风格
    - 色彩鲜艳但柔和
    - 形状简单明了
    - 适合3-8岁儿童观看
    - 图标风格：现代、友好、教育性
    - 尺寸：正方形，适合作为应用图标
    - 背景：透明或浅色背景
    
    描述参考：{apple_description}
    """
    
    # 请求数据 - ModelScope通用推理API格式
    data = {
        "inputs": prompt,
        "parameters": {
            "width": 512,
            "height": 512,
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "seed": random.randint(1, 1000000)
        }
    }
    
    try:
        print("正在生成苹果图标...")
        response = requests.post(api_url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            # ModelScope API可能返回直接图片数据或JSON
            try:
                result = response.json()
                if 'data' in result and 'image_url' in result['data']:
                    # 如果返回图片URL，下载图片
                    image_url = result['data']['image_url']
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        with open(output_path, 'wb') as f:
                            f.write(image_response.content)
                        print(f"苹果图标已成功保存到: {output_path}")
                        return True
                    else:
                        print(f"图片下载失败，状态码: {image_response.status_code}")
                        return False
                else:
                    print("API响应中没有图片URL")
                    return False
            except:
                # 如果返回直接图片数据
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"苹果图标已成功保存到: {output_path}")
                return True
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return False

if __name__ == "__main__":
    success = generate_apple_icon()
    if success:
        print("图标生成完成！")
    else:
        print("图标生成失败！")