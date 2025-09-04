class Car {
  final String carName;
  final String carEnglishName;
  final String carDescription;
  final String carType;
  final String carImagePath;
  final String chineseAudioPath;
  final String englishAudioPath;
  final String? carEnglishPronunciation;
  final String? carAmericanPronunciation;

  Car({
    required this.carName,
    required this.carEnglishName,
    required this.carDescription,
    required this.carType,
    required this.carImagePath,
    required this.chineseAudioPath,
    required this.englishAudioPath,
    this.carEnglishPronunciation,
    this.carAmericanPronunciation,
  });

  // 从JSON创建Car对象
  factory Car.fromJson(Map<String, dynamic> json) {
    // 获取原始路径
    String imagePath = json['car-image-path'] ?? '';
    String chineseAudio = json['chinese-audio-path'] ?? '';
    String englishAudio = json['english-audio-path'] ?? '';
    
    // 确保资源路径以"assets/"开头
    if (imagePath.isNotEmpty && !imagePath.startsWith('assets/')) {
      imagePath = 'assets/$imagePath';
    }
    if (chineseAudio.isNotEmpty && !chineseAudio.startsWith('assets/')) {
      chineseAudio = 'assets/$chineseAudio';
    }
    if (englishAudio.isNotEmpty && !englishAudio.startsWith('assets/')) {
      englishAudio = 'assets/$englishAudio';
    }
    
    return Car(
      carName: json['car-name'] ?? '',
      carEnglishName: json['car-english-name'] ?? '',
      carDescription: json['car-description'] ?? '',
      carType: json['car-type'] ?? '',
      carImagePath: imagePath,
      chineseAudioPath: chineseAudio,
      englishAudioPath: englishAudio,
      carEnglishPronunciation: json['car-english-pronunciation'],
      carAmericanPronunciation: json['car-american-pronunciation'],
    );
  }

  // 将Car对象转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'car-name': carName,
      'car-english-name': carEnglishName,
      'car-description': carDescription,
      'car-type': carType,
      'car-image-path': carImagePath,
      'chinese-audio-path': chineseAudioPath,
      'english-audio-path': englishAudioPath,
      'car-english-pronunciation': carEnglishPronunciation,
      'car-american-pronunciation': carAmericanPronunciation,
    };
  }

  @override
  String toString() {
    return 'Car(carName: $carName, carEnglishName: $carEnglishName)';
  }
}