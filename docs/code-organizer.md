# Code Organizer 注释规范

## 概述
Code Organizer 是一个用于组织和注释代码的扩展，帮助开发者更好地理解和维护代码结构。本规范定义了在项目中使用的注释格式和约定。

## 注释类型

### 1. 文件级别注释
在每个文件的开头添加文件级别的注释，描述文件的用途、作者、创建日期等信息。

```typescript
/**
 * @file 文件名
 * @description 文件描述
 * @author 作者名
 * @date 创建日期
 * @version 版本号
 */
```

### 2. 区域/块级别注释
使用区域注释将代码组织成逻辑块，便于阅读和理解。

```typescript
// #region 区域名称
// 区域描述
// 代码块...
// #endregion
```

### 3. 函数/方法级别注释
为每个函数或方法添加详细的注释，包括功能描述、参数说明、返回值等。

```typescript
/**
 * 函数功能描述
 * @param 参数名 - 参数描述
 * @returns 返回值描述
 * @throws 可能抛出的异常
 */
```

### 4. 行级别注释
对于复杂的逻辑或重要的代码行，添加行级别注释。

```typescript
// 注释说明
const result = complexCalculation();
```

### 5. TODO 注释
标记需要完成的任务或改进点。

```typescript
// TODO: 任务描述
// FIXME: 需要修复的问题
// NOTE: 重要提示
```

## 注释示例

### TypeScript 文件示例

```typescript
/**
 * @file car.ts
 * @description 汽车相关的状态管理
 * @author Developer
 * @date 2023-01-01
 * @version 1.0.0
 */

import { defineStore } from 'pinia';

// #region Store 定义
// 定义汽车相关的状态管理
export const useCarStore = defineStore('car', () => {
  // #endregion

  // #region 状态定义
  // 定义响应式状态
  const cars = ref<Car[]>([]);
  // #endregion

  // #region 计算属性
  // 定义计算属性
  const currentCar = computed<Car>(() => {
    return cars.value[currentIndex.value] || {} as Car;
  });
  // #endregion

  // #region 方法定义
  /**
   * 设置汽车数据
   * @param newCars - 新的汽车数据数组
   */
  const setCars = (newCars: Car[]) => {
    cars.value = newCars;
  };
  // #endregion
});
```

### Vue 文件示例

```vue
<template>
  <!-- #region 页面头部 -->
  <!-- 包含标题和搜索按钮 -->
  <div class="header">
    <h1>儿童早教学习卡片</h1>
    <button class="search-btn" @click="goToSearch">搜索</button>
  </div>
  <!-- #endregion -->
</template>

<script setup lang="ts">
/**
 * @file Home.vue
 * @description 主页面组件
 * @author Developer
 * @date 2023-01-01
 * @version 1.0.0
 */

import { ref } from 'vue';

// #region 触摸事件处理
// 处理触摸开始、移动和结束事件
const handleTouchStart = (e: TouchEvent) => {
  // TODO: 添加触摸开始处理逻辑
};
// #endregion
</script>

<style lang="scss" scoped>
/* #region 页面样式 */
/* 定义页面的基本样式 */
.home-page {
  width: 100%;
  height: 100vh;
}
/* #endregion */
</style>
```

## 最佳实践

1. **保持注释更新**：当代码发生变化时，及时更新相关注释
2. **避免过度注释**：不要为显而易见的代码添加注释
3. **使用清晰的语言**：使用简洁明了的语言描述代码功能
4. **保持一致性**：在整个项目中使用相同的注释风格
5. **添加示例**：对于复杂的函数，可以添加使用示例

## 工具集成

Code Organizer 扩展可以与以下工具集成：
- VS Code
- WebStorm
- 其他支持代码折叠的编辑器

通过使用这些注释规范，可以大大提高代码的可读性和可维护性。