#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
儿童鼓励音频生成脚本
生成儿童学习应用中的鼓励音频文件
"""

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

def generate_applaud_audio(text, output_path, voice_type="chinese", config=None):
    """
    调用微软TTS生成鼓励音频文件
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

def main():
    """主函数"""
    print("开始生成儿童鼓励音频...")
    
    try:
        # 加载配置
        config = load_config()
        print("配置文件加载成功")
        
        # 确保audios目录存在
        Path('kid_car_flutter/assets/audios').mkdir(exist_ok=True)
        
        # 鼓励语列表
        encourage_texts = {
            "chinese": [
                "太棒了！",
                "你真聪明！",
                "做得很好！",
                "继续加油！",
                "你真厉害！",
                "好样的！",
                "你真棒！",
                "真不错！",
                "非常好！",
                "再接再厉！"
            ],
            "english": [
                "Excellent!",
                "You're so smart!",
                "Great job!",
                "Keep it up!",
                "You're amazing!",
                "Well done!",
                "You're awesome!",
                "Nice work!",
                "Very good!",
                "Keep going!"
            ]
        }
        
        # 生成中文鼓励音频
        print("\n生成中文鼓励音频...")
        for i, text in enumerate(encourage_texts["chinese"], 1):
            filename = f"kid_car_flutter/assets/audios/applaud_zh_{i:02d}.mp3"
            print(f"生成第 {i}/{len(encourage_texts['chinese'])} 个中文鼓励音频: {text}")
            
            if generate_applaud_audio(text, filename, "chinese", config):
                print(f"  ✓ 成功生成: {filename}")
            else:
                print(f"  ✗ 生成失败: {text}")
            
            # 添加短暂延迟，避免API调用过于频繁
            time.sleep(1)
        
        # 生成英文鼓励音频
        print("\n生成英文鼓励音频...")
        for i, text in enumerate(encourage_texts["english"], 1):
            filename = f"kid_car_flutter/assets/audios/applaud_en_{i:02d}.mp3"
            print(f"生成第 {i}/{len(encourage_texts['english'])} 个英文鼓励音频: {text}")
            
            if generate_applaud_audio(text, filename, "english", config):
                print(f"  ✓ 成功生成: {filename}")
            else:
                print(f"  ✗ 生成失败: {text}")
            
            # 添加短暂延迟，避免API调用过于频繁
            time.sleep(1)
        
        print("\n鼓励音频生成完成！")
        print(f"共生成 {len(encourage_texts['chinese'])} 个中文鼓励音频")
        print(f"共生成 {len(encourage_texts['english'])} 个英文鼓励音频")
        print(f"音频文件保存在: kid_car_flutter/assets/audios/")
        
    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
    except yaml.YAMLError as e:
        print(f"YAML解析错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    main()