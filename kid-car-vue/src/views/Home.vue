<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCarStore } from '@/store/car';

const router = useRouter();
const carStore = useCarStore();

// 触摸相关变量
const touchStartX = ref<number>(0);
const touchEndX = ref<number>(0);
const isSwiping = ref<boolean>(false);

// 处理触摸开始事件
const handleTouchStart = (e: TouchEvent) => {
  touchStartX.value = e.changedTouches[0].screenX;
  isSwiping.value = true;
};

// 处理触摸移动事件
const handleTouchMove = (e: TouchEvent) => {
  if (!isSwiping.value) return;
  
  touchEndX.value = e.changedTouches[0].screenX;
  const diffX = touchStartX.value - touchEndX.value;
  
  // 添加滑动效果
  const carImage = document.querySelector('.car-image') as HTMLElement;
  if (carImage) {
    carImage.style.transform = `translateX(${-diffX * 0.5}px)`;
    carImage.style.transition = 'none';
  }
};

// 处理触摸结束事件
const handleTouchEnd = () => {
  if (!isSwiping.value) return;
  
  isSwiping.value = false;
  const diffX = touchStartX.value - touchEndX.value;
  
  // 重置图片位置
  const carImage = document.querySelector('.car-image') as HTMLElement;
  if (carImage) {
    carImage.style.transform = 'translateX(0)';
    carImage.style.transition = 'transform 0.3s ease';
  }
  
  // 判断滑动方向
  if (Math.abs(diffX) > 50) { // 滑动距离超过50px才认为是有效滑动
    if (diffX > 0) {
      // 向左滑动，下一个汽车
      carStore.nextCar();
    } else {
      // 向右滑动，上一个汽车
      carStore.prevCar();
    }
  }
};

// 处理汽车图片点击事件
const handleCarClick = async () => {
  if (!carStore.isPlayingAudio) {
    await carStore.playCarAudio();
  }
};

// 导航到搜索页面
const goToSearch = () => {
  router.push('/search');
};

// 处理键盘事件
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'ArrowLeft') {
    carStore.prevCar();
  } else if (e.key === 'ArrowRight') {
    carStore.nextCar();
  } else if (e.key === ' ' || e.key === 'Enter') {
    handleCarClick();
  }
};

onMounted(() => {
  // 添加键盘事件监听
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  // 移除键盘事件监听
  window.removeEventListener('keydown', handleKeyDown);
});
</script>

<template>
  <div class="home-page">
    <div class="header">
      <h1>儿童早教学习卡片</h1>
      <button class="search-btn" @click="goToSearch">
        <span class="search-icon">🔍</span>
        搜索
      </button>
    </div>
    
    <div class="car-container">
      <div 
        class="car-card"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
      >
        <div class="car-image-container" @click="handleCarClick">
          <img 
            :src="carStore.currentCar.image" 
            :alt="carStore.currentCar.name"
            class="car-image"
            :class="{ 'playing': carStore.isPlayingAudio }"
          />
          <div v-if="carStore.isPlayingAudio" class="audio-indicator">
            <div class="audio-wave"></div>
            <div class="audio-wave"></div>
            <div class="audio-wave"></div>
          </div>
        </div>
        
        <div class="car-info">
          <h2 class="car-name">{{ carStore.currentCar.name }}</h2>
          <p class="car-name-en">{{ carStore.currentCar.nameEn }}</p>
          <p class="car-desc">{{ carStore.currentCar.desc }}</p>
          <p class="car-desc-en">{{ carStore.currentCar.descEn }}</p>
          <div class="car-pronounce">
            <span>中文发音: {{ carStore.currentCar.pronounce }}</span>
            <span>英文发音: {{ carStore.currentCar.pronounceEn }}</span>
          </div>
          <div class="car-type">
            类型: {{ carStore.currentCar.type }}
          </div>
        </div>
      </div>
      
      <div class="navigation">
        <button 
          class="nav-btn prev-btn" 
          @click="carStore.prevCar"
          :disabled="carStore.currentIndex === 0"
        >
          上一张
        </button>
        <div class="car-counter">
          {{ carStore.currentIndex + 1 }} / {{ carStore.cars.length }}
        </div>
        <button 
          class="nav-btn next-btn" 
          @click="carStore.nextCar"
          :disabled="carStore.currentIndex === carStore.cars.length - 1"
        >
          下一张
        </button>
      </div>
    </div>
    
    <div class="tips">
      <p>💡 提示: 点击图片播放音频，左右滑动切换汽车</p>
      <p>⌨️ 键盘操作: ← → 切换汽车，空格/回车播放音频</p>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.home-page {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
  overflow: hidden;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #4CAF50;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  
  h1 {
    font-size: 20px;
    font-weight: bold;
    margin: 0;
  }
  
  .search-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background-color: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 20px;
    color: white;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      background-color: rgba(255, 255, 255, 0.3);
    }
    
    &:active {
      transform: scale(0.95);
    }
    
    .search-icon {
      font-size: 16px;
    }
  }
}

.car-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow-y: auto;
}

.car-card {
  width: 100%;
  max-width: 400px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 20px;
}

.car-image-container {
  position: relative;
  width: 100%;
  height: 250px;
  background-color: #f0f0f0;
  cursor: pointer;
  overflow: hidden;
  
  &:active {
    transform: scale(0.98);
  }
}

.car-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.3s ease;
  
  &.playing {
    animation: pulse 1.5s infinite;
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.audio-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 4px;
  
  .audio-wave {
    width: 4px;
    height: 20px;
    background-color: #4CAF50;
    border-radius: 2px;
    animation: wave 1s infinite ease-in-out;
    
    &:nth-child(2) {
      animation-delay: 0.2s;
      height: 30px;
    }
    
    &:nth-child(3) {
      animation-delay: 0.4s;
      height: 15px;
    }
  }
}

@keyframes wave {
  0%, 100% {
    transform: scaleY(0.5);
  }
  50% {
    transform: scaleY(1);
  }
}

.car-info {
  padding: 20px;
  
  .car-name {
    font-size: 24px;
    font-weight: bold;
    margin: 0 0 8px 0;
    color: #333;
  }
  
  .car-name-en {
    font-size: 18px;
    color: #666;
    margin: 0 0 16px 0;
    font-style: italic;
  }
  
  .car-desc, .car-desc-en {
    font-size: 16px;
    line-height: 1.5;
    margin: 8px 0;
    color: #555;
  }
  
  .car-pronounce {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin: 16px 0;
    font-size: 14px;
    color: #777;
  }
  
  .car-type {
    font-size: 14px;
    color: #4CAF50;
    font-weight: bold;
    margin-top: 16px;
    padding: 6px 12px;
    background-color: rgba(76, 175, 80, 0.1);
    border-radius: 20px;
    display: inline-block;
  }
}

.navigation {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  
  .nav-btn {
    padding: 10px 20px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover:not(:disabled) {
      background-color: #45a049;
    }
    
    &:active:not(:disabled) {
      transform: scale(0.95);
    }
    
    &:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
    }
  }
  
  .car-counter {
    font-size: 16px;
    color: #666;
    min-width: 80px;
    text-align: center;
  }
}

.tips {
  padding: 16px;
  background-color: rgba(0, 0, 0, 0.05);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  
  p {
    font-size: 14px;
    color: #666;
    margin: 4px 0;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .header {
    h1 {
      font-size: 18px;
    }
    
    .search-btn {
      font-size: 12px;
      padding: 6px 12px;
      
      .search-icon {
        font-size: 14px;
      }
    }
  }
  
  .car-info {
    .car-name {
      font-size: 20px;
    }
    
    .car-name-en {
      font-size: 16px;
    }
    
    .car-desc, .car-desc-en {
      font-size: 14px;
    }
  }
  
  .navigation {
    .nav-btn {
      padding: 8px 16px;
      font-size: 14px;
    }
    
    .car-counter {
      font-size: 14px;
    }
  }
}
</style>