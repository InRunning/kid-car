import os
import json
import time
import yaml
from PIL import Image
from io import BytesIO
from google import genai # 更新的导入方式
from google.genai import types

# 配置常量
CONFIG_FILE = "local.yaml"
CAR_JSON_FILE = "kid_car_flutter/assets/car.json"
IMAGES_DIR = "kid_car_flutter/assets/images"

# API密钥配置
API_KEY = None

def load_config():
    """加载配置文件，优先从环境变量读取API密钥"""
    global API_KEY
    
    # 1. 优先从环境变量 GEMINI_API_KEY 读取
    env_api_key = os.environ.get("GEMINI_API_KEY")
    if env_api_key:
        API_KEY = env_api_key
        print("✓ 已从环境变量 GEMINI_API_KEY 加载API密钥")
        return
    
    # 2. 如果环境变量未设置，则从 local.yaml 文件读取
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if "Gemini" in config and "ApiKey" in config["Gemini"]:
            API_KEY = config["Gemini"]["ApiKey"]
            print("✓ 已从 local.yaml 文件加载API密钥")
        else:
            print("⚠ 在 local.yaml 中未找到 Gemini API 密钥")
            API_KEY = None # 确保API_KEY为None
    except FileNotFoundError:
        print(f"⚠ 配置文件 {CONFIG_FILE} 未找到")
        API_KEY = None
    except Exception as e:
        print(f"⚠ 读取配置文件 {CONFIG_FILE} 时发生错误: {e}")
        API_KEY = None

def get_api_key():
    """获取API密钥，如果未加载则尝试加载"""
    if API_KEY is None: # 如果API_KEY尚未被设置（为None），则尝试加载
        load_config()
    
    if not API_KEY: # 再次检查，确保加载后API_KEY是有效的
        error_message = (
            "错误：没有可用的 Gemini API 密钥。\n"
            "请通过以下任一方式设置：\n"
            "1. 设置环境变量 GEMINI_API_KEY (推荐)\n"
            "   例如 (在终端运行): export GEMINI_API_KEY='YOUR_API_KEY'\n"
            "2. 在 local.yaml 文件中配置 Gemini.ApiKey"
        )
        raise ValueError(error_message)
    return API_KEY

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
    """使用新版Gemini API生成车辆图片"""
    # 创建提示词，明确要求不要出现人物
    prompt = f"一辆{car_name}，{car_type}，卡通风格，儿童友好，明亮色彩，简洁背景，不要出现人物，不要出现人，不要有人脸，不要有人形"
    
    try:
        # 获取API密钥，这会触发load_config()如果API_KEY为None
        api_key = get_api_key()

        # 使用新版API初始化客户端
        # 注意：新版客户端会自动尝试从 GOOGLE_GENAI_API_KEY 环境变量读取密钥
        # 但我们显式传入以确保使用我们配置的密钥
        client = genai.Client(api_key=api_key)

        # 发送图片生成请求
        response = client.models.generate_images(
            model='imagen-3.0-generate-001',  # 使用合适的图像生成模型
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1, # 每次只生成一张图
                # 可以添加其他配置，如尺寸等，如果需要的话
                # aspect_ratio="1:1",
                # output_format="png",
            )
        )
        
        if not response.generated_images:
            print(f"✗ 图片生成失败: {car_name}, 响应中未包含图片")
            return None

        # 获取生成的图片
        generated_image = response.generated_images[0]
        
        # 确保images目录存在
        os.makedirs(IMAGES_DIR, exist_ok=True)
        
        # 生成图片文件名，使用PNG格式以获得更好质量
        image_filename = f"{car_name}_{car_type}.png"
        image_path = os.path.join(IMAGES_DIR, image_filename)
        
        # 保存图片
        # generated_image.image.image_bytes 是原始图像数据
        with open(image_path, "wb") as f:
            f.write(generated_image.image.image_bytes)
        
        print(f"✓ 图片保存成功: {image_path}")
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