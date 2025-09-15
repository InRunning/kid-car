export interface Car {
  id: string;
  name: string;
  nameEn: string;
  desc: string;
  descEn: string;
  pronounce: string;
  pronounceEn: string;
  image: string;
  audio: string;
  audioEn: string;
  type: string;
}

export interface CarType {
  id: string;
  name: string;
  count: number;
}

export interface CarState {
  cars: Car[];
  carTypes: CarType[];
  currentIndex: number;
  searchQuery: string;
  selectedType: string | null;
  isPlayingAudio: boolean;
}

export interface CarActions {
  setCars: (cars: Car[]) => void;
  setCarTypes: (carTypes: CarType[]) => void;
  setCurrentIndex: (index: number) => void;
  setSearchQuery: (query: string) => void;
  setSelectedType: (type: string | null) => void;
  setIsPlayingAudio: (isPlaying: boolean) => void;
  nextCar: () => void;
  prevCar: () => void;
  goToCar: (index: number) => void;
  playAudio: (audioPath: string) => Promise<void>;
  playCarAudio: () => Promise<void>;
}