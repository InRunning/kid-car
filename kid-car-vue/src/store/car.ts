/**
 * @file car.ts
 * @description 汽车相关的状态管理，使用 Pinia 管理汽车数据、类型、搜索和音频播放功能
 * @author Developer
 * @date 2023-01-01
 * @version 1.0.0
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Car, CarType, CarState, CarActions } from '@/types/car';
import carData from '@/data/car.json';

export const useCarStore = defineStore('car', () => {
  // #region 状态定义
  // 定义响应式状态，存储汽车数据、类型、当前索引、搜索查询等
  // 状态
  const cars = ref<Car[]>([]);
  const carTypes = ref<CarType[]>([]);
  const currentIndex = ref<number>(0);
  const searchQuery = ref<string>('');
  const selectedType = ref<string | null>(null);
  const isPlayingAudio = ref<boolean>(false);
  const currentAudio = ref<HTMLAudioElement | null>(null);
  // 播放会话标识，用于在切换图片或重新播放时取消之前的播放序列
  const playbackToken = ref<number>(0);

  // 生成新的播放会话标识
  const newPlaybackToken = () => {
    playbackToken.value += 1;
    return playbackToken.value;
  };
  // #endregion

  // #region 计算属性
  // 定义计算属性，用于派生状态，如当前汽车、过滤后的汽车列表等
  // 计算属性
  const currentCar = computed<Car>(() => {
    return cars.value[currentIndex.value] || {} as Car;
  });

  const filteredCars = computed<Car[]>(() => {
    let result = cars.value;
    
    if (selectedType.value) {
      result = result.filter(car => car.type === selectedType.value);
    }
    
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase().trim();
      result = result.filter(car => 
        car.name.toLowerCase().includes(query) || 
        car.nameEn.toLowerCase().includes(query) ||
        car.type.toLowerCase().includes(query)
      );
    }
    
    return result;
  });

  const filteredCarTypes = computed<CarType[]>(() => {
    if (!searchQuery.value.trim()) {
      return carTypes.value;
    }
    
    const query = searchQuery.value.toLowerCase().trim();
    return carTypes.value.filter(type => 
      type.name.toLowerCase().includes(query)
    );
  });
  // #endregion

  // #region 动作定义
  // 定义动作方法，用于修改状态和处理业务逻辑
  // 动作
  /**
   * 设置汽车数据
   * @param newCars - 新的汽车数据数组
   */
  const setCars = (newCars: Car[]) => {
    cars.value = newCars;
    // 保存当前索引到本地存储
    saveCurrentIndexToStorage();
  };

  /**
   * 设置汽车类型数据
   * @param newCarTypes - 新的汽车类型数组
   */
  const setCarTypes = (newCarTypes: CarType[]) => {
    carTypes.value = newCarTypes;
  };

  /**
   * 设置当前汽车索引
   * @param index - 新的索引值
   */
  const setCurrentIndex = (index: number) => {
    if (index >= 0 && index < cars.value.length) {
      currentIndex.value = index;
      saveCurrentIndexToStorage();
    }
  };

  /**
   * 设置搜索查询
   * @param query - 搜索查询字符串
   */
  const setSearchQuery = (query: string) => {
    searchQuery.value = query;
  };

  /**
   * 设置选中的汽车类型
   * @param type - 汽车类型，null 表示全部类型
   */
  const setSelectedType = (type: string | null) => {
    selectedType.value = type;
  };

  /**
   * 设置音频播放状态
   * @param isPlaying - 是否正在播放音频
   */
  const setIsPlayingAudio = (isPlaying: boolean) => {
    isPlayingAudio.value = isPlaying;
  };

  /**
   * 停止当前正在播放的音频
   */
  const stopCurrentAudio = () => {
    if (currentAudio.value) {
      currentAudio.value.pause();
      currentAudio.value.currentTime = 0;
      currentAudio.value = null;
    }
    setIsPlayingAudio(false);
  };

  // 取消当前播放序列（用于切换图片或重新开始播放）
  const cancelPlayback = () => {
    // 先递增 token，后续序列检查到不匹配将直接退出
    newPlaybackToken();
    stopCurrentAudio();
  };

  /**
   * 切换到下一个汽车
   */
  const nextCar = () => {
    if (currentIndex.value < cars.value.length - 1) {
      // 立即停止并取消之前的播放序列
      cancelPlayback();
      currentIndex.value++;
      saveCurrentIndexToStorage();
      // 直接播放当前图片音频（无延迟）
      playCarAudio();
    }
  };

  const prevCar = () => {
    if (currentIndex.value > 0) {
      // 立即停止并取消之前的播放序列
      cancelPlayback();
      currentIndex.value--;
      saveCurrentIndexToStorage();
      // 直接播放当前图片音频（无延迟）
      playCarAudio();
    }
  };

  const goToCar = (index: number) => {
    if (index >= 0 && index < cars.value.length && index !== currentIndex.value) {
      // 立即停止并取消之前的播放序列
      cancelPlayback();
      currentIndex.value = index;
      saveCurrentIndexToStorage();
      // 直接播放当前图片音频（无延迟）
      playCarAudio();
    }
  };

  const playAudio = async (audioPath: string, token: number): Promise<void> => {
    try {
      // 如果序列已被取消，直接结束
      if (token !== playbackToken.value) return;

      const audio = new Audio(audioPath);
      currentAudio.value = audio;
      await audio.play();
      await new Promise<void>((resolve) => {
        // 结束、暂停或错误都认为当前段落已结束（便于取消时尽快退出）
        audio.onended = () => resolve();
        audio.onpause = () => resolve();
        audio.onerror = () => resolve();
      });
      currentAudio.value = null;
    } catch (error) {
      console.error('播放音频失败:', error);
      currentAudio.value = null;
      throw error;
    }
  };

  const playCarAudio = async (): Promise<void> => {
    const car = currentCar.value;
    if (!car.audio || !car.audioEn) return;

    // 启动新的播放会话，取消之前的序列
    const token = newPlaybackToken();

    try {
      setIsPlayingAudio(true);
      // 先播放英文音频三遍
      for (let i = 0; i < 3; i++) {
        if (token !== playbackToken.value) return; // 已被取消
        await playAudio(car.audioEn, token);
        if (token !== playbackToken.value) return; // 已被取消
      }
      // 再播放中文音频一遍
      if (token !== playbackToken.value) return; // 已被取消
      await playAudio(car.audio, token);
    } catch (error) {
      console.error('播放汽车音频失败:', error);
    } finally {
      // 只在当前会话仍然有效时重置播放状态
      if (token === playbackToken.value) {
        setIsPlayingAudio(false);
      }
    }
  };

  // 本地存储相关
  const saveCurrentIndexToStorage = () => {
    try {
      localStorage.setItem('kid-car-current-index', currentIndex.value.toString());
    } catch (error) {
      console.error('保存当前索引到本地存储失败:', error);
    }
  };

  const loadCurrentIndexFromStorage = () => {
    try {
      const savedIndex = localStorage.getItem('kid-car-current-index');
      if (savedIndex !== null) {
        const index = parseInt(savedIndex, 10);
        if (!isNaN(index) && index >= 0 && index < cars.value.length) {
          currentIndex.value = index;
        }
      }
    } catch (error) {
      console.error('从本地存储加载当前索引失败:', error);
    }
  };

  // 初始化数据
  const initializeData = () => {
    // 从JSON文件加载数据并转换格式
    if (carData && Array.isArray(carData)) {
      cars.value = carData.map((item: any, index: number) => ({
        id: `car-${index}`,
        name: item['car-name'],
        nameEn: item['car-english-name'],
        desc: item['car-description'] || '',
        descEn: '', // 如果没有英文描述，留空
        pronounce: item['car-english-pronunciation'] || '',
        pronounceEn: item['car-american-pronunciation'] || '',
        image: `/${item['car-image-path']}`,
        audio: `/${item['chinese-audio-path']}`,
        audioEn: `/${item['english-audio-path']}`,
        type: item['car-type']
      }));

      // 生成汽车类型数据
      const typeMap = new Map<string, number>();
      cars.value.forEach((car: Car) => {
        const count = typeMap.get(car.type) || 0;
        typeMap.set(car.type, count + 1);
      });

      carTypes.value = Array.from(typeMap.entries()).map(([name, count]) => ({
        id: name.toLowerCase().replace(/\s+/g, '-'),
        name,
        count
      }));
    }

    // 从本地存储加载当前索引
    loadCurrentIndexFromStorage();
  };

  // 初始化
  initializeData();

  return {
    // 状态
    cars,
    carTypes,
    currentIndex,
    searchQuery,
    selectedType,
    isPlayingAudio,
    currentAudio,
    
    // 计算属性
    currentCar,
    filteredCars,
    filteredCarTypes,
    
    // 动作
    setCars,
    setCarTypes,
    setCurrentIndex,
    setSearchQuery,
    setSelectedType,
    setIsPlayingAudio,
    stopCurrentAudio,
    cancelPlayback,
    nextCar,
    prevCar,
    goToCar,
    playCarAudio
  };
});
