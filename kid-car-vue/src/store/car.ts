import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Car, CarType, CarState, CarActions } from '@/types/car';
import carData from '@/data/car.json';

export const useCarStore = defineStore('car', () => {
  // 状态
  const cars = ref<Car[]>([]);
  const carTypes = ref<CarType[]>([]);
  const currentIndex = ref<number>(0);
  const searchQuery = ref<string>('');
  const selectedType = ref<string | null>(null);
  const isPlayingAudio = ref<boolean>(false);

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

  // 动作
  const setCars = (newCars: Car[]) => {
    cars.value = newCars;
    // 保存当前索引到本地存储
    saveCurrentIndexToStorage();
  };

  const setCarTypes = (newCarTypes: CarType[]) => {
    carTypes.value = newCarTypes;
  };

  const setCurrentIndex = (index: number) => {
    if (index >= 0 && index < cars.value.length) {
      currentIndex.value = index;
      saveCurrentIndexToStorage();
    }
  };

  const setSearchQuery = (query: string) => {
    searchQuery.value = query;
  };

  const setSelectedType = (type: string | null) => {
    selectedType.value = type;
  };

  const setIsPlayingAudio = (isPlaying: boolean) => {
    isPlayingAudio.value = isPlaying;
  };

  const nextCar = () => {
    if (currentIndex.value < cars.value.length - 1) {
      currentIndex.value++;
      saveCurrentIndexToStorage();
    }
  };

  const prevCar = () => {
    if (currentIndex.value > 0) {
      currentIndex.value--;
      saveCurrentIndexToStorage();
    }
  };

  const goToCar = (index: number) => {
    if (index >= 0 && index < cars.value.length) {
      currentIndex.value = index;
      saveCurrentIndexToStorage();
    }
  };

  const playAudio = async (audioPath: string): Promise<void> => {
    try {
      setIsPlayingAudio(true);
      const audio = new Audio(audioPath);
      await audio.play();
      await new Promise(resolve => {
        audio.onended = resolve;
      });
    } catch (error) {
      console.error('播放音频失败:', error);
    } finally {
      setIsPlayingAudio(false);
    }
  };

  const playCarAudio = async (): Promise<void> => {
    const car = currentCar.value;
    if (!car.audio || !car.audioEn) return;
    
    try {
      setIsPlayingAudio(true);
      // 先播放中文音频
      await playAudio(car.audio);
      // 再播放英文音频
      await playAudio(car.audioEn);
    } catch (error) {
      console.error('播放汽车音频失败:', error);
    } finally {
      setIsPlayingAudio(false);
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
    // 从JSON文件加载数据
    if (carData && carData.cars) {
      cars.value = carData.cars;
      
      // 生成汽车类型数据
      const typeMap = new Map<string, number>();
      cars.value.forEach(car => {
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
    nextCar,
    prevCar,
    goToCar,
    playAudio,
    playCarAudio
  };
});