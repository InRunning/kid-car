# 项目功能介绍

这是一个用于儿童认识车以及听英语和中文车名发音的工具，

# 项目实现步骤

配置文件是 local.yaml，配置需要从这个文件读取，不要讲配置写死在代码里面

1. 首先生成一个 car-name.py 的脚本，调用魔搭的 Zhipu 模型来生成 car-name, car-english-name,car-description，具体调用方式可以参考 docs/Zhipu.py，然后将结果
   存进 kid_car_flutter/assets/car.json 文件中，要求每生成一个就要更新一次 json，然后这个需要支持下次可以恢复运行

2. 编写一个 generate-image.py 的脚本，读取 kid_car_flutter/assets/car.json 的数据，调用魔搭的 Qwen-Image 模型来生成
   对应图片，具体调用方式可以参考 docs/Qwen-Image.py, 要求不要出现人物，生成的图片存进 kid_car_flutter/assets/images 目录中，然后修改 kid_car_flutter/assets/car.json 中对应的 car-image-path成assets/images/xxx,要求每生成一个就要更新一次 json，然后这个需要支持下次可以恢复运行

3. 编写一个 doubao-generate-image.py 的脚本，读取 kid_car_flutter/assets/car.json的数据，调用豆包的文生图模型，具体调用方式参考 docs/豆包文生图python.py，要求不要出现人物，生成的图片存进 kid_car_flutter/assets/images 目录中，然后修改 kid_car_flutter/assets/car.json 中对应的 car-image-path成assets/images/xxx,要求每生成一个就要更新一次 json，然后这个需要支持下次可以恢复运行

4. 参考  generate-image.py写generate-image-gemini.py的脚本，只将模型换成nano banana即可，其它输入输出保持不变，apikey的配置从local.yaml中读取

4. 再编写一个check_image_audio.py的脚本，用于检查kid_car_flutter/assets/car.json中的    "car-image-path",
    "chinese-audio-path",
    "english-audio-path"这些对应的音频文件是否存在，不存在打印出来告警


3. 编写一个 generate-icon.py 的脚本，用于生成kid-car这个app的icon，也是调用魔搭的Qwen-Image模型

4. 编写一个 generate-kid-applaud.py的脚本

3. 编写一个 generate-audio.py 的脚本，读取 kid_car_flutter/assets/car.json 的数据，参考ref-docs/微软语音合成.sh调用微软的tts，分别生成对应的中文发音以及英文发音文件存进kid_car_flutter/assets/audios目录下，然后修改 kid_car_flutter/assets/car.json 中对应的 chinese-audio-path, english-audio-path,要求每生成一个就要更新一次 json，然后这个需要支持下次可以恢复运行

4. 使用flutter再实现app，读取 kid_car_flutter/assets/car.json的数据，要求首页是展示car图片，然后点击会有微微放大效果并播放英文音频三遍+中文音频一遍，之后重新进入app要能进入之前car，然后支持左右划动来切换不同的car，第二个导航栏是搜索，展示对应的car列表供选择，car列表要根据car-type进行分类，也可以搜索car和car-type进行选择，选择后路由直接跳转到首页，然后对应car替换成选择的car



