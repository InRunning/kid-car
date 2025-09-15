<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCarStore } from '@/store/car';

const router = useRouter();
const carStore = useCarStore();

// 搜索输入
const searchInput = ref<HTMLInputElement | null>(null);
const isSearchFocused = ref(false);

// 计算属性
const hasSearchQuery = computed(() => carStore.searchQuery.trim() !== '');
const hasSelectedType = computed(() => carStore.selectedType !== null);

// 处理搜索输入
const handleSearchInput = (e: Event) => {
  const target = e.target as HTMLInputElement;
  carStore.setSearchQuery(target.value);
};

// 清除搜索
const clearSearch = () => {
  carStore.setSearchQuery('');
  if (searchInput.value) {
    searchInput.value.focus();
  }
};

// 选择汽车类型
const selectType = (type: string | null) => {
  carStore.setSelectedType(type);
};

// 查看汽车详情
const viewCarDetail = (index: number) => {
  carStore.goToCar(index);
  router.push('/');
};

// 返回首页
const goBack = () => {
  router.back();
};

// 处理键盘事件
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') {
    goBack();
  }
};

onMounted(() => {
  // 聚焦搜索输入
  if (searchInput.value) {
    searchInput.value.focus();
  }
  
  // 添加键盘事件监听
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  // 移除键盘事件监听
  window.removeEventListener('keydown', handleKeyDown);
});
</script>

<template>
  <div class="search-page">
    <div class="header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <div class="search-container">
        <input
          ref="searchInput"
          type="text"
          placeholder="搜索汽车名称或类型..."
          class="search-input"
          :value="carStore.searchQuery"
          @input="handleSearchInput"
          @focus="isSearchFocused = true"
          @blur="isSearchFocused = false"
        />
        <button 
          v-if="hasSearchQuery" 
          class="clear-btn" 
          @click="clearSearch"
        >
          ×
        </button>
      </div>
    </div>
    
    <div class="content">
      <!-- 汽车类型列表 -->
      <div v-if="!hasSearchQuery" class="section">
        <h2 class="section-title">汽车类型</h2>
        <div class="type-list">
          <div 
            v-for="type in carStore.carTypes" 
            :key="type.id"
            class="type-item"
            :class="{ 'active': carStore.selectedType === type.name }"
            @click="selectType(carStore.selectedType === type.name ? null : type.name)"
          >
            <div class="type-info">
              <h3 class="type-name">{{ type.name }}</h3>
              <span class="type-count">{{ type.count }} 辆</span>
            </div>
            <div class="type-icon">🚗</div>
          </div>
        </div>
      </div>
      
      <!-- 搜索结果 -->
      <div v-if="hasSearchQuery" class="section">
        <h2 class="section-title">
          搜索结果
          <span class="result-count">({{ carStore.filteredCars.length }} 辆)</span>
        </h2>
        
        <!-- 汽车类型搜索结果 -->
        <div v-if="carStore.filteredCarTypes.length > 0" class="search-types">
          <h3 class="subsection-title">相关类型</h3>
          <div class="type-list compact">
            <div 
              v-for="type in carStore.filteredCarTypes" 
              :key="type.id"
              class="type-item"
              :class="{ 'active': carStore.selectedType === type.name }"
              @click="selectType(carStore.selectedType === type.name ? null : type.name)"
            >
              <div class="type-info">
                <h3 class="type-name">{{ type.name }}</h3>
                <span class="type-count">{{ type.count }} 辆</span>
              </div>
              <div class="type-icon">🚗</div>
            </div>
          </div>
        </div>
        
        <!-- 汽车搜索结果 -->
        <div v-if="carStore.filteredCars.length > 0" class="search-results">
          <h3 class="subsection-title">相关汽车</h3>
          <div class="car-grid">
            <div 
              v-for="(car, index) in carStore.filteredCars" 
              :key="car.id"
              class="car-item"
              @click="viewCarDetail(carStore.cars.findIndex(c => c.id === car.id))"
            >
              <div class="car-image-container">
                <img 
                  :src="car.image" 
                  :alt="car.name"
                  class="car-image"
                />
              </div>
              <div class="car-info">
                <h3 class="car-name">{{ car.name }}</h3>
                <p class="car-name-en">{{ car.nameEn }}</p>
                <div class="car-type-tag">{{ car.type }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 无搜索结果 -->
        <div v-if="carStore.filteredCars.length === 0 && carStore.filteredCarTypes.length === 0" class="no-results">
          <div class="no-results-icon">🔍</div>
          <p class="no-results-text">没有找到相关汽车</p>
          <button class="retry-btn" @click="clearSearch">重新搜索</button>
        </div>
      </div>
      
      <!-- 按类型筛选的汽车列表 -->
      <div v-if="hasSelectedType && !hasSearchQuery" class="section">
        <h2 class="section-title">
          {{ carStore.selectedType }}
          <span class="result-count">({{ carStore.filteredCars.length }} 辆)</span>
          <button class="clear-filter-btn" @click="selectType(null)">清除筛选</button>
        </h2>
        
        <div v-if="carStore.filteredCars.length > 0" class="car-grid">
          <div 
            v-for="(car, index) in carStore.filteredCars" 
            :key="car.id"
            class="car-item"
            @click="viewCarDetail(carStore.cars.findIndex(c => c.id === car.id))"
          >
            <div class="car-image-container">
              <img 
                :src="car.image" 
                :alt="car.name"
                class="car-image"
              />
            </div>
            <div class="car-info">
              <h3 class="car-name">{{ car.name }}</h3>
              <p class="car-name-en">{{ car.nameEn }}</p>
            </div>
          </div>
        </div>
        
        <div v-else class="no-results">
          <div class="no-results-icon">🚗</div>
          <p class="no-results-text">该类型下没有汽车</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.search-page {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  padding: 16px;
  background-color: #4CAF50;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  gap: 12px;
  
  .back-btn {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    font-size: 18px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    
    &:hover {
      background-color: rgba(255, 255, 255, 0.3);
    }
    
    &:active {
      transform: scale(0.95);
    }
  }
  
  .search-container {
    flex: 1;
    position: relative;
    
    .search-input {
      width: 100%;
      padding: 10px 40px 10px 16px;
      border: none;
      border-radius: 20px;
      font-size: 16px;
      background-color: rgba(255, 255, 255, 0.9);
      outline: none;
      
      &::placeholder {
        color: #999;
      }
    }
    
    .clear-btn {
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background-color: #ccc;
      border: none;
      color: white;
      font-size: 16px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
      
      &:hover {
        background-color: #999;
      }
    }
  }
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.section {
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  
  .result-count {
    font-size: 14px;
    color: #666;
    font-weight: normal;
  }
  
  .clear-filter-btn {
    margin-left: auto;
    padding: 4px 12px;
    background-color: #f44336;
    color: white;
    border: none;
    border-radius: 16px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      background-color: #d32f2f;
    }
  }
}

.subsection-title {
  font-size: 16px;
  font-weight: bold;
  color: #555;
  margin: 16px 0 12px 0;
}

.type-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  
  &.compact {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}

.type-item {
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  
  &:active {
    transform: scale(0.98);
  }
  
  &.active {
    background-color: #4CAF50;
    color: white;
    
    .type-count {
      color: rgba(255, 255, 255, 0.8);
    }
  }
  
  .type-info {
    flex: 1;
    
    .type-name {
      font-size: 16px;
      font-weight: bold;
      margin: 0 0 4px 0;
    }
    
    .type-count {
      font-size: 12px;
      color: #666;
    }
  }
  
  .type-icon {
    font-size: 24px;
  }
}

.car-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.car-item {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  
  &:active {
    transform: scale(0.98);
  }
  
  .car-image-container {
    width: 100%;
    height: 120px;
    background-color: #f0f0f0;
    overflow: hidden;
    
    .car-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  
  .car-info {
    padding: 12px;
    
    .car-name {
      font-size: 16px;
      font-weight: bold;
      margin: 0 0 4px 0;
      color: #333;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .car-name-en {
      font-size: 14px;
      color: #666;
      margin: 0 0 8px 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .car-type-tag {
      font-size: 12px;
      color: #4CAF50;
      background-color: rgba(76, 175, 80, 0.1);
      padding: 2px 8px;
      border-radius: 10px;
      display: inline-block;
    }
  }
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  
  .no-results-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .no-results-text {
    font-size: 16px;
    color: #666;
    margin-bottom: 16px;
  }
  
  .retry-btn {
    padding: 8px 16px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      background-color: #45a049;
    }
  }
}

@media (max-width: 480px) {
  .header {
    padding: 12px;
    
    .back-btn {
      width: 36px;
      height: 36px;
      font-size: 16px;
    }
    
    .search-container {
      .search-input {
        padding: 8px 36px 8px 14px;
        font-size: 14px;
      }
      
      .clear-btn {
        width: 20px;
        height: 20px;
        font-size: 14px;
      }
    }
  }
  
  .content {
    padding: 12px;
  }
  
  .section-title {
    font-size: 18px;
  }
  
  .type-list {
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    
    &.compact {
      grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    }
  }
  
  .car-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
}
</style>