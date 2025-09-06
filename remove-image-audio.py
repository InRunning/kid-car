#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
from pathlib import Path

def get_referenced_files(json_file):
    """从JSON文件中获取所有引用的图片和音频文件路径"""
    referenced_files = set()
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data:
            # 获取图片路径
            if 'car-image-path' in item and item['car-image-path']:
                referenced_files.add(item['car-image-path'])
            
            # 获取音频路径
            if 'chinese-audio-path' in item and item['chinese-audio-path']:
                referenced_files.add(item['chinese-audio-path'])
            if 'english-audio-path' in item and item['english-audio-path']:
                referenced_files.add(item['english-audio-path'])
                    
    except Exception as e:
        print(f"读取JSON文件时出错: {e}")
        sys.exit(1)
        
    return referenced_files

def get_actual_files(directory):
    """获取目录中的所有文件"""
    actual_files = set()
    
    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        return actual_files
        
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 获取相对于assets目录的路径
            file_path = os.path.relpath(os.path.join(root, file), 'kid_car_flutter')
            actual_files.add(file_path)
            
    return actual_files

def find_unused_files(referenced_files, actual_files):
    """找出未使用的文件"""
    return actual_files - referenced_files

def delete_files(files_to_delete):
    """删除指定的文件"""
    deleted_count = 0
    failed_count = 0
    
    for file_path in files_to_delete:
        full_path = os.path.join('kid_car_flutter', file_path)
        try:
            os.remove(full_path)
            print(f"已删除: {file_path}")
            deleted_count += 1
        except Exception as e:
            print(f"删除失败 {file_path}: {e}")
            failed_count += 1
            
    return deleted_count, failed_count

def main():
    # 文件路径
    json_file = 'kid_car_flutter/assets/car.json'
    audio_dir = 'kid_car_flutter/assets/audios'
    image_dir = 'kid_car_flutter/assets/images'
    
    print("正在分析文件...")
    
    # 获取JSON中引用的文件
    referenced_files = get_referenced_files(json_file)
    print(f"JSON中引用的文件数量: {len(referenced_files)}")
    
    # 获取实际的音频文件
    actual_audio_files = get_actual_files(audio_dir)
    print(f"实际音频文件数量: {len(actual_audio_files)}")
    
    # 获取实际的图片文件
    actual_image_files = get_actual_files(image_dir)
    print(f"实际图片文件数量: {len(actual_image_files)}")
    
    # 合并所有实际文件
    all_actual_files = actual_audio_files | actual_image_files
    print(f"实际文件总数: {len(all_actual_files)}")
    
    # 找出未使用的文件
    unused_files = find_unused_files(referenced_files, all_actual_files)
    print(f"\n未使用的文件数量: {len(unused_files)}")
    
    if unused_files:
        print("\n未使用的文件列表:")
        for i, file_path in enumerate(sorted(unused_files), 1):
            print(f"{i}. {file_path}")
        
        # 询问用户是否要删除这些文件
        print(f"\n总共发现 {len(unused_files)} 个未使用的文件")
        response = input("是否要删除这些文件？(y/n): ").strip().lower()
        
        if response == 'y':
            print("\n正在删除文件...")
            deleted_count, failed_count = delete_files(unused_files)
            print(f"\n删除完成: 成功删除 {deleted_count} 个文件, 失败 {failed_count} 个文件")
        else:
            print("取消删除操作")
    else:
        print("没有发现未使用的文件")

if __name__ == "__main__":
    main()