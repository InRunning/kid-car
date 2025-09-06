# 项目功能介绍

这是一个用于儿童认识车以及听英语和中文车名发音的工具，

# 项目实现步骤

配置文件是 local.yaml，配置需要从这个文件读取，不要讲配置写死在代码里面

1. 首先生成一个 car-name.py 的脚本，调用魔搭的 Zhipu 模型来生成 car-name, car-english-name,car-description，具体调用方式可以参考 docs/Zhipu.py，然后将结果
   存进 kid_car_flutter/assets/car.json 文件中，要求每生成一个就要更新一次 json，然后这个需要支持下次可以恢复运行

2. 编写一个 generate-image.py 的脚本，读取 kid_car_flutter/assets/car.json 的数据，调用魔搭的 Qwen-Image 模型来生成
   对应图片，具体调用方式可以参考 docs/Qwen-Image.py, 要求不要出现人物，生成的图片存进 kid_car_flutter/assets/images 目录中，然后修改 kid_car_flutter/assets/car.json 中对应的 car-image-path 成 assets/images/xxx,要求每生成一个就要更新一次 json，然后这个需要支持下次可以恢复运行

3. 编写一个 doubao-generate-image.py 的脚本，读取 kid_car_flutter/assets/car.json 的数据，调用豆包的文生图模型，具体调用方式参考 docs/豆包文生图 python.py，要求不要出现人物，生成的图片存进 kid_car_flutter/assets/images 目录中，然后修改 kid_car_flutter/assets/car.json 中对应的 car-image-path 成 assets/images/xxx,要求每生成一个就要更新一次 json，然后这个需要支持下次可以恢复运行

4. 参考 generate-image.py 写 generate-image-gemini.py 的脚本，只将模型换成 nano banana 即可，其它输入输出保持不变，apikey 的配置从 local.yaml 中读取

5. 再编写一个 check_image_audio.py 的脚本，用于检查 kid_car_flutter/assets/car.json 中的 "car-image-path",
   "chinese-audio-path",
   "english-audio-path"这些对应的音频文件是否存在，不存在打印出来告警

6. 编写一个 generate-icon.py 的脚本，用于生成 kid-car 这个 app 的 icon，也是调用魔搭的 Qwen-Image 模型

7. 编写一个 generate-kid-applaud.py 的脚本

8. 编写一个 remove-image-audio.py 的脚本，读取 kid_car_flutter/assets/car.json 的数据，然后检查对应 kid_car_flutter/assets/audios 和 kid_car_flutter/assets/images 中有没有多余的不存在 kid_car_flutter/assets/car.json 里面的 image-path 和 audio_path 的文件，如果有多余的，先显示出来数量和具体的文件名，然后等待用户确认进行删除

9. 编写一个 generate-audio.py 的脚本，读取 kid_car_flutter/assets/car.json 的数据，参考 ref-docs/微软语音合成.sh 调用微软的 tts，分别生成对应的中文发音以及英文发音文件存进 kid_car_flutter/assets/audios 目录下，然后修改 kid_car_flutter/assets/car.json 中对应的 chinese-audio-path, english-audio-path,要求每生成一个就要更新一次 json，然后这个需要支持下次可以恢复运行

10. 使用 flutter 再实现 app，读取 kid_car_flutter/assets/car.json 的数据，要求首页是展示 car 图片，然后点击会有微微放大效果并播放英文音频三遍+中文音频一遍，之后重新进入 app 要能进入之前 car，然后支持左右划动来切换不同的 car，切换后立即播放英文音频三遍+中文音频一遍，第二个导航栏是搜索，展示对应的 car 列表供选择，car 列表要根据 car-type 进行分类，也可以搜索 car 和 car-type 进行选择，选择后路由直接跳转到首页，然后对应 car 替换成选择的 car
