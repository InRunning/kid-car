#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import shutil
from pathlib import Path

def is_valid_car_entry(car_entry):
    """
    判断车辆条目是否有效
    - 排除字母类型（如A、B、C等）
    - 可以根据需要添加其他规则
    """
    car_name = car_entry.get("car-name", "")
    car_type = car_entry.get("car-type", "")
    
    # 排除类型为"字母"的条目
    if car_type == "字母":
        print(f"排除字母类型条目: {car_name}")
        return False
    
    # 排除单个字母作为名称的条目（不区分大小写）
    if len(car_name) == 1 and car_name.isalpha():
        print(f"排除单字母名称条目: {car_name}")
        return False
    
    # 排除名称中包含"字母"的条目
    if "字母" in car_name:
        print(f"排除名称包含'字母'的条目: {car_name}")
        return False
    
    # 可以添加更多的排除规则
    # 例如：排除名称长度小于2的条目
    if len(car_name) < 2:
        print(f"排除名称过短的条目: {car_name}")
        return False
    
    return True

def get_file_path(asset_path):
    """
    根据资源路径获取实际文件路径
    """
    # 移除路径前的"assets/"前缀
    if asset_path.startswith("assets/"):
        relative_path = asset_path[8:]  # 去掉"assets/"
        return os.path.join("kid_car_flutter", "assets", relative_path)
    return asset_path

def delete_resource_file(file_path):
    """
    删除资源文件
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已删除文件: {file_path}")
            return True
        else:
            print(f"文件不存在，跳过删除: {file_path}")
            return False
    except Exception as e:
        print(f"删除文件失败: {file_path}, 错误: {e}")
        return False

def process_car_json(json_file_path, dry_run=False):
    """
    处理车辆JSON文件，删除无效条目和相关资源
    """
    # 读取JSON文件
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            car_data = json.load(f)
    except Exception as e:
        print(f"读取JSON文件失败: {json_file_path}, 错误: {e}")
        return
    
    if not isinstance(car_data, list):
        print(f"JSON数据格式不正确，应为数组")
        return
    
    print(f"处理 {len(car_data)} 个车辆条目...")
    
    # 筛选有效的车辆条目
    valid_entries = []
    deleted_entries = []
    
    for entry in car_data:
        if is_valid_car_entry(entry):
            valid_entries.append(entry)
        else:
            deleted_entries.append(entry)
    
    # 输出统计信息
    print(f"有效条目: {len(valid_entries)}")
    print(f"无效条目: {len(deleted_entries)}")
    
    # 如果只是预览，不实际删除
    if dry_run:
        print("\n=== 预览模式 - 不会实际删除文件 ===")
        for entry in deleted_entries:
            print(f"将删除: {entry.get('car-name', '未知')}")
            car_image = get_file_path(entry.get("car-image-path", ""))
            chinese_audio = get_file_path(entry.get("chinese-audio-path", ""))
            english_audio = get_file_path(entry.get("english-audio-path", ""))
            print(f"  - 图片: {car_image}")
            print(f"  - 中文音频: {chinese_audio}")
            print(f"  - 英文音频: {english_audio}")
        return
    
    # 实际删除无效条目和相关资源
    print("\n=== 开始删除无效条目和资源 ===")
    for entry in deleted_entries:
        car_name = entry.get("car-name", "未知")
        print(f"\n处理条目: {car_name}")
        
        # 删除相关资源文件
        car_image = get_file_path(entry.get("car-image-path", ""))
        chinese_audio = get_file_path(entry.get("chinese-audio-path", ""))
        english_audio = get_file_path(entry.get("english-audio-path", ""))
        
        delete_resource_file(car_image)
        delete_resource_file(chinese_audio)
        delete_resource_file(english_audio)
    
    # 更新JSON文件
    if deleted_entries:
        try:
            # 创建备份文件
            backup_path = f"{json_file_path}.bak"
            shutil.copy2(json_file_path, backup_path)
            print(f"\n已创建备份文件: {backup_path}")
            
            # 写入更新后的JSON文件
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(valid_entries, f, ensure_ascii=False, indent=2)
            
            print(f"已更新JSON文件，保留 {len(valid_entries)} 个有效条目")
        except Exception as e:
            print(f"写入JSON文件失败: {e}")

def main():
    import argparse
    
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="AI审查脚本 - 清理无效的车辆条目和相关资源")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际删除文件")
    parser.add_argument("--json-path", default="kid_car_flutter/assets/car.json", help="车辆JSON文件路径")
    
    args = parser.parse_args()
    
    # 检查JSON文件是否存在
    if not os.path.exists(args.json_path):
        print(f"错误: JSON文件不存在: {args.json_path}")
        return
    
    print(f"AI审查脚本 - 处理文件: {args.json_path}")
    print(f"模式: {'预览（不删除文件）' if args.dry_run else '实际删除'}")
    
    # 处理JSON文件
    process_car_json(args.json_path, dry_run=args.dry_run)
    
    print("\n处理完成！")

if __name__ == "__main__":
    main()