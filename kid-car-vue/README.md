# 儿童汽车学习卡片 - Vue3版

这是一个基于Vue3开发的儿童汽车学习卡片应用，帮助儿童认识各种汽车及其名称、发音等信息。

## 功能特点

- 🚗 展示各种汽车图片和详细信息
- 🔊 点击图片播放中英文发音
- 👆 支持左右滑动切换汽车
- 💾 记住上次访问的汽车
- 🔍 搜索功能，可按汽车名称或类型搜索
- 📱 响应式设计，适配各种屏幕尺寸

## 技术栈

- Vue 3 (Composition API)
- TypeScript
- SCSS
- Pinia (状态管理)
- Vue Router (路由)
- Vite (构建工具)

## 项目结构

```
kid-car-vue/
├── src/
│   ├── assets/        # 静态资源
│   ├── components/    # 公共组件
│   ├── data/          # 数据文件
│   ├── router/        # 路由配置
│   ├── store/         # 状态管理
│   ├── types/         # TypeScript类型定义
│   ├── views/         # 页面组件
│   ├── App.vue        # 根组件
│   ├── main.ts        # 入口文件
│   └── env.d.ts       # 环境变量声明
├── index.html         # HTML模板
├── package.json       # 项目依赖
├── tsconfig.json      # TypeScript配置
├── vite.config.ts     # Vite配置
└── README.md          # 项目说明
```

## 开发和构建

### 安装依赖

```bash
npm install
```

### 开发环境运行

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 使用说明

### 首页

- 点击汽车图片播放中英文发音
- 左右滑动切换汽车
- 使用左右按钮或键盘方向键切换汽车
- 点击右上角搜索按钮进入搜索页面

### 搜索页面

- 在搜索框中输入汽车名称或类型进行搜索
- 点击汽车类型可以筛选该类型的汽车
- 点击汽车卡片可以查看该汽车的详细信息

### 键盘快捷键

- `←` `→`: 切换汽车
- `空格` 或 `回车`: 播放音频
- `Esc`: 返回上一页

## 数据格式

汽车数据存储在 `src/data/car.json` 文件中，格式如下：

```json
{
  "cars": [
    {
      "id": "1",
      "name": "轿车",
      "nameEn": "Sedan",
      "desc": "一种有固定车顶的载客汽车",
      "descEn": "A passenger car with a fixed roof",
      "pronounce": "jiào chē",
      "pronounceEn": "/sɪˈdæn/",
      "image": "assets/images/sedan.png",
      "audio": "assets/audio/sedan.mp3",
      "audioEn": "assets/audio/sedan_en.mp3",
      "type": "乘用车"
    }
  ]
}
```

## 注意事项

- 确保所有图片和音频文件路径正确
- 音频文件建议使用MP3格式，兼容性更好
- 本项目使用了本地存储来记住上次访问的汽车，请确保浏览器支持localStorage

## 浏览器兼容性

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 许可证

MIT