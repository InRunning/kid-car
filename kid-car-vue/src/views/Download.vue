<script setup lang="ts">
/**
 * @file Download.vue
 * @description 下载页面组件，提供kid-car.apk文件的下载功能
 * @author Developer
 * @date 2023-01-01
 * @version 1.0.0
 */

import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isDownloading = ref<boolean>(false);
const downloadProgress = ref<number>(0);
const downloadComplete = ref<boolean>(false);

// APK文件路径
const apkFilePath = '/kid-car.apk';
const apkFileName = 'kid-car.apk';
const apkFileSize = '25.6 MB'; // 假设的文件大小

/**
 * 处理APK文件下载
 */
const downloadApk = () => {
  isDownloading.value = true;
  downloadProgress.value = 0;
  downloadComplete.value = false;
  
  // 模拟下载进度
  const interval = setInterval(() => {
    downloadProgress.value += Math.random() * 15;
    
    if (downloadProgress.value >= 100) {
      downloadProgress.value = 100;
      isDownloading.value = false;
      downloadComplete.value = true;
      clearInterval(interval);
      
      // 实际下载文件
      const link = document.createElement('a');
      link.href = apkFilePath;
      link.download = apkFileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }, 300);
};

/**
 * 返回首页
 */
const goToHome = () => {
  router.push('/');
};
</script>

<template>
  <div class="download-page">
    <!-- 页面头部 -->
    <div class="header">
      <button class="back-btn" @click="goToHome">
        <span class="back-icon">←</span>
        返回
      </button>
      <h1>下载应用</h1>
      <div class="header-spacer"></div>
    </div>
    
    <!-- 下载内容区域 -->
    <div class="download-container">
      <!-- 应用图标和名称 -->
      <div class="app-info">
        <div class="app-icon">
          <span class="icon-car">🚗</span>
        </div>
        <h2 class="app-name">儿童英语学习卡片</h2>
        <p class="app-version">版本 1.0.0</p>
        <p class="app-size">文件大小: {{ apkFileSize }}</p>
      </div>
      
      <!-- 下载按钮和进度 -->
      <div class="download-section">
        <button 
          class="download-btn" 
          @click="downloadApk"
          :disabled="isDownloading"
        >
          <span v-if="!isDownloading && !downloadComplete" class="btn-text">
            <span class="download-icon">⬇️</span>
            下载 APK
          </span>
          <span v-else-if="isDownloading" class="btn-text">
            <span class="loading-icon">⏳</span>
            下载中... {{ Math.round(downloadProgress) }}%
          </span>
          <span v-else class="btn-text">
            <span class="success-icon">✅</span>
            下载完成
          </span>
        </button>
        
        <!-- 下载进度条 -->
        <div v-if="isDownloading" class="progress-container">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: downloadProgress + '%' }"
            ></div>
          </div>
        </div>
      </div>
      
      <!-- 应用介绍 -->
      <div class="app-description">
        <h3>应用介绍</h3>
        <p>儿童英语学习卡片是一款专为儿童设计的教育应用，通过丰富的图片和音频，帮助儿童学习英语，提高英语听说能力。</p>
        
        <div class="features">
          <div class="feature-item">
            <span class="feature-icon">🎨</span>
            <span>丰富的学习图片</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">🔊</span>
            <span>标准中英文发音</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">👆</span>
            <span>简单易用的操作</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">📱</span>
            <span>支持多种学习模式</span>
          </div>
        </div>
      </div>
      
      <!-- 安装说明 -->
      <div class="install-instructions">
        <h3>安装说明</h3>
        <ol>
          <li>点击上方"下载 APK"按钮下载应用</li>
          <li>下载完成后，打开文件进行安装</li>
          <li>如果提示"未知来源应用"，请在设置中允许安装未知来源的应用</li>
          <li>安装完成后即可使用</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.download-page {
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
  
  .back-btn {
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
    
    .back-icon {
      font-size: 16px;
    }
  }
  
  .header-spacer {
    width: 60px; /* 与返回按钮宽度相同，用于保持标题居中 */
  }
}

.download-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  overflow-y: auto;
  gap: 24px;
}

.app-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  
  .app-icon {
    width: 80px;
    height: 80px;
    background-color: #4CAF50;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    
    .icon-car {
      font-size: 40px;
    }
  }
  
  .app-name {
    font-size: 24px;
    font-weight: bold;
    margin: 0 0 8px 0;
    color: #333;
  }
  
  .app-version {
    font-size: 16px;
    color: #666;
    margin: 0 0 4px 0;
  }
  
  .app-size {
    font-size: 14px;
    color: #999;
    margin: 0;
  }
}

.download-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 300px;
  
  .download-btn {
    width: 100%;
    padding: 16px 24px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    
    &:hover:not(:disabled) {
      background-color: #45a049;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }
    
    &:active:not(:disabled) {
      transform: translateY(0);
    }
    
    &:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
    }
    
    .btn-text {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .download-icon,
    .loading-icon,
    .success-icon {
      font-size: 20px;
    }
  }
  
  .progress-container {
    width: 100%;
    margin-top: 16px;
    
    .progress-bar {
      width: 100%;
      height: 8px;
      background-color: #e0e0e0;
      border-radius: 4px;
      overflow: hidden;
      
      .progress-fill {
        height: 100%;
        background-color: #4CAF50;
        border-radius: 4px;
        transition: width 0.3s ease;
      }
    }
  }
}

.app-description {
  width: 100%;
  max-width: 400px;
  background-color: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  h3 {
    font-size: 18px;
    font-weight: bold;
    margin: 0 0 12px 0;
    color: #333;
  }
  
  p {
    font-size: 14px;
    line-height: 1.6;
    color: #666;
    margin: 0 0 16px 0;
  }
  
  .features {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    
    .feature-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      color: #555;
      
      .feature-icon {
        font-size: 18px;
      }
    }
  }
}

.install-instructions {
  width: 100%;
  max-width: 400px;
  background-color: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  h3 {
    font-size: 18px;
    font-weight: bold;
    margin: 0 0 12px 0;
    color: #333;
  }
  
  ol {
    padding-left: 20px;
    margin: 0;
    
    li {
      font-size: 14px;
      line-height: 1.6;
      color: #666;
      margin-bottom: 8px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

@media (max-width: 480px) {
  .header {
    h1 {
      font-size: 18px;
    }
    
    .back-btn {
      font-size: 12px;
      padding: 6px 12px;
      
      .back-icon {
        font-size: 14px;
      }
    }
  }
  
  .app-info {
    .app-name {
      font-size: 20px;
    }
    
    .app-version {
      font-size: 14px;
    }
    
    .app-size {
      font-size: 12px;
    }
  }
  
  .download-section {
    .download-btn {
      font-size: 16px;
      padding: 14px 20px;
    }
  }
  
  .app-description,
  .install-instructions {
    h3 {
      font-size: 16px;
    }
    
    p,
    li {
      font-size: 13px;
    }
  }
}
</style>