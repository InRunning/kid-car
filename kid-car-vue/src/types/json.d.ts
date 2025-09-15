declare module '*.json' {
  const value: any;
  export default value;
}

declare module '@/data/car.json' {
  interface CarData {
    cars: Array<{
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
    }>;
  }
  
  const data: CarData;
  export default data;
}