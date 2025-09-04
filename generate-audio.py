#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import yaml
import os
import requests
import time
from pathlib import Path
from urllib.parse import quote

def load_config():
    """加载配置文件"""
    with open('local.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_car_data():
    """加载车辆数据"""
    with open('kid_car_flutter/assets/car.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_car_data(car_data):
    """保存车辆数据"""
    with open('kid_car_flutter/assets/car.json', 'w', encoding='utf-8') as f:
        json.dump(car_data, f, ensure_ascii=False, indent=2)

def generate_audio(text, output_path, voice_type="chinese", config=None):
    """
    调用微软TTS生成音频文件
    使用Python requests库替代curl
    """
    if config is None:
        raise ValueError("配置不能为空")
    
    # 从配置中获取Edge设置
    edge_config = config.get('Edge', {})
    base_url = edge_config.get('BaseUrl', 'https://ms-ra-forwarder-silk-ten.vercel.app')
    token = edge_config.get('Token', '')
    
    if not token:
        raise ValueError("Edge配置中缺少Token")
    
    # 根据语言类型选择不同的语音
    if voice_type == "chinese":
        voice = "Microsoft+Server+Speech+Text+to+Speech+Voice+(zh-CN,+XiaoxiaoNeural)"
    else:  # english
        voice = "Microsoft+Server+Speech+Text+to+Speech+Voice+(en-US,+JennyNeural)"
    
    # 构建请求URL - 手动构建查询字符串以避免requests的自动编码
    query_string = f"voice={voice}&volume=0&rate=0&pitch=0&text={quote(text)}"
    api_url = f"{base_url}/api/text-to-speech?{query_string}"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        print(f"  请求URL: {api_url}")
        
        # 发送GET请求
        response = requests.get(api_url, headers=headers, stream=True)
        response.raise_for_status()
        
        # 保存音频文件
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # 检查文件是否成功创建且大小大于0
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"  成功生成音频文件: {output_path} (大小: {os.path.getsize(output_path)} bytes)")
            return True
        else:
            print(f"  生成音频文件失败: {output_path}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  调用TTS API失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  响应状态码: {e.response.status_code}")
            print(f"  响应内容: {e.response.text}")
        return False
    except Exception as e:
        print(f"  生成音频时发生错误: {e}")
        return False

def process_car_audio(car_data, config):
    """处理车辆音频生成"""
    # 确保audios目录存在
    Path('kid_car_flutter/assets/audios').mkdir(exist_ok=True)
    
    total_cars = len(car_data)
    processed_count = 0
    
    for i, car in enumerate(car_data):
        print(f"处理第 {i+1}/{total_cars} 个车辆: {car['car-name']}")
        
        # 检查是否已经生成了音频文件
        chinese_audio_generated = car.get('chinese-audio-path', '').strip() != ''
        english_audio_generated = car.get('english-audio-path', '').strip() != ''
        
        if chinese_audio_generated and english_audio_generated:
            print(f"  跳过 {car['car-name']} - 音频文件已存在")
            processed_count += 1
            continue
        
        # 生成中文音频
        if not chinese_audio_generated:
            chinese_filename = f"kid_car_flutter/assets/audios/{car['car-name']}_zh.mp3"
            print(f"  生成中文音频: {chinese_filename}")
            
            if generate_audio(car['car-name'], chinese_filename, "chinese", config):
                car['chinese-audio-path'] = chinese_filename
                # 立即保存更新
                save_car_data(car_data)
                print(f"  已更新中文音频路径: {chinese_filename}")
            else:
                print(f"  中文音频生成失败，跳过此车辆")
                continue
        
        # 生成英文音频
        if not english_audio_generated:
            english_filename = f"kid_car_flutter/assets/audios/{car['car-english-name']}_en.mp3"
            print(f"  生成英文音频: {english_filename}")
            
            if generate_audio(car['car-english-name'], english_filename, "english", config):
                car['english-audio-path'] = english_filename
                # 立即保存更新
                save_car_data(car_data)
                print(f"  已更新英文音频路径: {english_filename}")
            else:
                print(f"  英文音频生成失败，跳过此车辆")
                continue
        
        processed_count += 1
        print(f"  完成 {car['car-name']} 的音频生成")
        
        # 添加短暂延迟，避免API调用过于频繁
        time.sleep(1)
    
    print(f"\n处理完成！共处理 {processed_count}/{total_cars} 个车辆")
    return car_data

def main():
    """主函数"""
    print("开始生成车辆音频文件...")
    
    try:
        # 加载配置
        config = load_config()
        print("配置文件加载成功")
        
        # 加载车辆数据
        car_data = load_car_data()
        print(f"加载了 {len(car_data)} 个车辆数据")
        
        # 处理音频生成
        updated_car_data = process_car_audio(car_data, config)
        
        # 最终保存
        save_car_data(updated_car_data)
        print("所有数据已保存")
        
        print("音频生成任务完成！")
        
    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
    except yaml.YAMLError as e:
        print(f"YAML解析错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    main()