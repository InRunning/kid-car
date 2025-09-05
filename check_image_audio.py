#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
from pathlib import Path

def load_json_file(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"错误：文件 {file_path} 不是有效的JSON格式")
        return None
    except Exception as e:
        print(f"错误：加载文件 {file_path} 时发生异常：{str(e)}")
        return None

def check_file_exists(file_path, item_name, file_type):
    """检查文件是否存在"""
    if not file_path:
        print(f"警告：{item_name} 的 {file_type} 路径为空")
        return False
    
    # 转换路径为相对于当前工作目录的绝对路径
    abs_path = Path(file_path)
    if not abs_path.is_absolute():
        abs_path = Path.cwd() / "kid_car_flutter" / file_path
    
    if abs_path.exists():
        return True
    else:
        print(f"警告：{item_name} 的 {file_type} 文件不存在: {file_path}")
        return False

def check_image_audio_files(json_file_path):
    """检查JSON文件中的图片和音频文件是否存在"""
    print(f"开始检查文件: {json_file_path}")
    
    # 加载JSON数据
    data = load_json_file(json_file_path)
    if data is None:
        return False
    
    if not isinstance(data, list):
        print(f"错误：JSON文件内容格式不正确，应该是一个数组")
        return False
    
    print(f"共找到 {len(data)} 个条目需要检查")
    
    missing_files = 0
    total_checks = 0
    
    for item in data:
        item_name = item.get("car-name", "未知项目")
        
        # 检查图片文件
        image_path = item.get("car-image-path", "")
        total_checks += 1
        if not check_file_exists(image_path, item_name, "图片"):
            missing_files += 1
        
        # 检查中文音频文件
        chinese_audio_path = item.get("chinese-audio-path", "")
        total_checks += 1
        if not check_file_exists(chinese_audio_path, item_name, "中文音频"):
            missing_files += 1
        
        # 检查英文音频文件
        english_audio_path = item.get("english-audio-path", "")
        total_checks += 1
        if not check_file_exists(english_audio_path, item_name, "英文音频"):
            missing_files += 1
    
    print("\n检查完成！")
    print(f"总共检查了 {len(data)} 个条目，{total_checks} 个文件")
    print(f"缺失文件数量：{missing_files}")
    print(f"文件完整性：{((total_checks - missing_files) / total_checks * 100):.1f}%")
    
    if missing_files > 0:
        print("\n⚠️  发现缺失文件，请根据上述警告信息补充缺失的文件")
        return False
    else:
        print("\n✅ 所有文件检查通过，没有发现缺失文件")
        return True

def main():
    """主函数"""
    # 设置JSON文件路径
    json_file_path = "kid_car_flutter/assets/car.json"
    
    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        print(f"错误：找不到JSON文件 {json_file_path}")
        print("请确保文件路径正确，或者运行脚本时使用正确的当前工作目录")
        sys.exit(1)
    
    # 执行检查
    success = check_image_audio_files(json_file_path)
    
    # 根据检查结果设置退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()