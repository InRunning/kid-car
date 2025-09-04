#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用图标生成脚本
使用通义千问生成适合儿童学习车辆应用的图标
"""

import json
import os
import requests
import time
import yaml
from PIL import Image
from io import BytesIO
import shutil

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
    API_KEY = config['ModelScope']['ApiKeys'][0]  # 使用第一个API key
    IMAGE_MODEL = config['ModelScope']['ImageModel']
else:
    print("使用默认配置")
    BASE_URL = 'https://api-inference.modelscope.cn/'
    API_KEY = "ms-149e41d6-fb33-455d-bf45-86e8e97947b1"  # ModelScope Token
    IMAGE_MODEL = "Qwen/Qwen-Image-Edit"

# 确保icons目录存在
ICONS_DIR = 'icons'
if not os.path.exists(ICONS_DIR):
    os.makedirs(ICONS_DIR)

def create_headers():
    """创建请求头"""
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

def generate_app_icon():
    """生成应用图标"""
    # 构建图标生成提示词
    prompt = "儿童学习车辆应用的图标，卡通风格，包含多种车辆元素，色彩鲜艳，适合儿童，简洁明了，不要文字"
    
    print("正在生成应用图标...")
    
    try:
        # 发送图片生成请求
        response = requests.post(
            f"{BASE_URL}v1/images/generations",
            headers={**create_headers(), "X-ModelScope-Async-Mode": "true"},
            data=json.dumps({
                "model": IMAGE_MODEL,  # 使用配置中的图片生成模型
                "prompt": prompt,
                "n": 1,  # 生成1张图片
                "size": "1024x1024"  # 图片尺寸
            }, ensure_ascii=False).encode('utf-8')
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
            )
            result.raise_for_status()
            data = result.json()
            
            if data["task_status"] == "SUCCEED":
                # 下载生成的图片
                image_url = data["output_images"][0]
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                
                # 保存原始图片
                original_filename = "app_icon_original.png"
                original_path = os.path.join(ICONS_DIR, original_filename)
                
                with open(original_path, 'wb') as f:
                    f.write(image_response.content)
                
                print(f"✓ 图标生成成功: {original_path}")
                return original_path
                
            elif data["task_status"] == "FAILED":
                print(f"✗ 图标生成失败")
                return None
            
            # 等待5秒后重试
            time.sleep(5)
            attempts += 1
            
        print(f"✗ 图标生成超时")
        return None
        
    except Exception as e:
        print(f"生成图标时出错: {e}")
        return None

def resize_image(image_path, size):
    """调整图片尺寸"""
    try:
        with Image.open(image_path) as img:
            # 转换为RGBA模式以支持透明度
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 调整尺寸
            resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
            return resized_img
    except Exception as e:
        print(f"调整图片尺寸时出错: {e}")
        return None

def generate_android_icons(original_icon_path):
    """生成Android平台图标"""
    print("\n生成Android平台图标...")
    
    # Android图标尺寸配置
    android_sizes = {
        'mipmap-mdpi': 48,
        'mipmap-hdpi': 72,
        'mipmap-xhdpi': 96,
        'mipmap-xxhdpi': 144,
        'mipmap-xxxhdpi': 192
    }
    
    success_count = 0
    
    for dir_name, size in android_sizes.items():
        target_dir = os.path.join('kid_car_flutter', 'android', 'app', 'src', 'main', 'res', dir_name)
        target_path = os.path.join(target_dir, 'ic_launcher.png')
        
        # 检查是否已存在
        if os.path.exists(target_path):
            print(f"✓ Android图标已存在: {target_path}")
            success_count += 1
            continue
        
        # 调整尺寸
        resized_img = resize_image(original_icon_path, size)
        if resized_img:
            try:
                # 确保目录存在
                os.makedirs(target_dir, exist_ok=True)
                
                # 保存图片
                resized_img.save(target_path, 'PNG')
                print(f"✓ Android图标生成成功: {target_path}")
                success_count += 1
            except Exception as e:
                print(f"✗ 保存Android图标失败: {e}")
    
    return success_count

def generate_ios_icons(original_icon_path):
    """生成iOS平台图标"""
    print("\n生成iOS平台图标...")
    
    # iOS图标尺寸配置
    ios_sizes = {
        'Icon-App-20x20@1x.png': 20,
        'Icon-App-20x20@2x.png': 40,
        'Icon-App-20x20@3x.png': 60,
        'Icon-App-29x29@1x.png': 29,
        'Icon-App-29x29@2x.png': 58,
        'Icon-App-29x29@3x.png': 87,
        'Icon-App-40x40@1x.png': 40,
        'Icon-App-40x40@2x.png': 80,
        'Icon-App-40x40@3x.png': 120,
        'Icon-App-60x60@2x.png': 120,
        'Icon-App-60x60@3x.png': 180,
        'Icon-App-76x76@1x.png': 76,
        'Icon-App-76x76@2x.png': 152,
        'Icon-App-83.5x83.5@2x.png': 167,
        'Icon-App-1024x1024@1x.png': 1024
    }
    
    target_dir = os.path.join('kid_car_flutter', 'ios', 'Runner', 'Assets.xcassets', 'AppIcon.appiconset')
    success_count = 0
    
    for filename, size in ios_sizes.items():
        target_path = os.path.join(target_dir, filename)
        
        # 检查是否已存在
        if os.path.exists(target_path):
            print(f"✓ iOS图标已存在: {target_path}")
            success_count += 1
            continue
        
        # 调整尺寸
        resized_img = resize_image(original_icon_path, size)
        if resized_img:
            try:
                # 确保目录存在
                os.makedirs(target_dir, exist_ok=True)
                
                # 保存图片
                resized_img.save(target_path, 'PNG')
                print(f"✓ iOS图标生成成功: {target_path}")
                success_count += 1
            except Exception as e:
                print(f"✗ 保存iOS图标失败: {e}")
    
    return success_count

def generate_web_icons(original_icon_path):
    """生成Web平台图标"""
    print("\n生成Web平台图标...")
    
    # Web图标尺寸配置
    web_sizes = {
        'Icon-192.png': 192,
        'Icon-512.png': 512,
        'Icon-maskable-192.png': 192,
        'Icon-maskable-512.png': 512
    }
    
    target_dir = os.path.join('kid_car_flutter', 'web', 'icons')
    success_count = 0
    
    for filename, size in web_sizes.items():
        target_path = os.path.join(target_dir, filename)
        
        # 检查是否已存在
        if os.path.exists(target_path):
            print(f"✓ Web图标已存在: {target_path}")
            success_count += 1
            continue
        
        # 调整尺寸
        resized_img = resize_image(original_icon_path, size)
        if resized_img:
            try:
                # 确保目录存在
                os.makedirs(target_dir, exist_ok=True)
                
                # 保存图片
                resized_img.save(target_path, 'PNG')
                print(f"✓ Web图标生成成功: {target_path}")
                success_count += 1
            except Exception as e:
                print(f"✗ 保存Web图标失败: {e}")
    
    return success_count

def generate_macos_icons(original_icon_path):
    """生成macOS平台图标"""
    print("\n生成macOS平台图标...")
    
    # macOS图标尺寸配置
    macos_sizes = {
        'app_icon_16.png': 16,
        'app_icon_32.png': 32,
        'app_icon_64.png': 64,
        'app_icon_128.png': 128,
        'app_icon_256.png': 256,
        'app_icon_512.png': 512,
        'app_icon_1024.png': 1024
    }
    
    target_dir = os.path.join('kid_car_flutter', 'macos', 'Runner', 'Assets.xcassets', 'AppIcon.appiconset')
    success_count = 0
    
    for filename, size in macos_sizes.items():
        target_path = os.path.join(target_dir, filename)
        
        # 检查是否已存在
        if os.path.exists(target_path):
            print(f"✓ macOS图标已存在: {target_path}")
            success_count += 1
            continue
        
        # 调整尺寸
        resized_img = resize_image(original_icon_path, size)
        if resized_img:
            try:
                # 确保目录存在
                os.makedirs(target_dir, exist_ok=True)
                
                # 保存图片
                resized_img.save(target_path, 'PNG')
                print(f"✓ macOS图标生成成功: {target_path}")
                success_count += 1
            except Exception as e:
                print(f"✗ 保存macOS图标失败: {e}")
    
    return success_count

def generate_windows_icons(original_icon_path):
    """生成Windows平台图标"""
    print("\n生成Windows平台图标...")
    
    # Windows图标需要ICO格式，包含多种尺寸
    sizes = [16, 32, 48, 64, 128, 256]
    
    target_dir = os.path.join('kid_car_flutter', 'windows', 'runner', 'resources')
    target_path = os.path.join(target_dir, 'app_icon.ico')
    
    # 检查是否已存在
    if os.path.exists(target_path):
        print(f"✓ Windows图标已存在: {target_path}")
        return 1
    
    try:
        # 确保目录存在
        os.makedirs(target_dir, exist_ok=True)
        
        # 创建ICO文件
        from PIL import Image
        
        # 收集所有尺寸的图片
        images = []
        for size in sizes:
            resized_img = resize_image(original_icon_path, size)
            if resized_img:
                images.append(resized_img)
        
        if images:
            # 保存为ICO文件
            images[0].save(target_path, format='ICO', sizes=[(img.size[0], img.size[1]) for img in images])
            print(f"✓ Windows图标生成成功: {target_path}")
            return 1
        else:
            print(f"✗ 生成Windows图标失败")
            return 0
    except Exception as e:
        print(f"✗ 生成Windows图标时出错: {e}")
        return 0

def main():
    """主函数"""
    print("开始生成应用图标...")
    
    # 检查是否已经有原始图标
    original_icon_path = os.path.join(ICONS_DIR, "app_icon_original.png")
    if not os.path.exists(original_icon_path):
        # 生成原始图标
        original_icon_path = generate_app_icon()
        if not original_icon_path:
            print("生成原始图标失败，程序退出")
            return
    else:
        print(f"✓ 原始图标已存在: {original_icon_path}")
    
    # 生成各平台图标
    android_count = generate_android_icons(original_icon_path)
    ios_count = generate_ios_icons(original_icon_path)
    web_count = generate_web_icons(original_icon_path)
    macos_count = generate_macos_icons(original_icon_path)
    windows_count = generate_windows_icons(original_icon_path)
    
    total_count = android_count + ios_count + web_count + macos_count + windows_count
    total_expected = 5 + 14 + 4 + 7 + 1  # 各平台期望的图标数量
    
    print(f"\n完成！成功生成 {total_count}/{total_expected} 个平台图标")
    print(f"- Android: {android_count}/5")
    print(f"- iOS: {ios_count}/14")
    print(f"- Web: {web_count}/4")
    print(f"- macOS: {macos_count}/7")
    print(f"- Windows: {windows_count}/1")
    print(f"\n原始图标保存在: {original_icon_path}")

if __name__ == "__main__":
    main()