import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/car_model.dart';
import '../services/car_service.dart';

class CarProvider with ChangeNotifier {
  List<Car> _cars = [];
  Car? _currentCar;
  bool _isLoading = false;
  String _errorMessage = '';
  bool _isPlayingAudio = false;
  String _currentAudioType = '';

  List<Car> get cars => _cars;
  Car? get currentCar => _currentCar;
  bool get isLoading => _isLoading;
  String get errorMessage => _errorMessage;
  bool get isPlayingAudio => _isPlayingAudio;
  String get currentAudioType => _currentAudioType;

  // 加载车辆数据
  Future<void> loadCars() async {
    _isLoading = true;
    _errorMessage = '';
    notifyListeners();

    try {
      _cars = await CarService.loadCarsFromAssets();
      await loadLastCar();
    } catch (e) {
      _errorMessage = '加载车辆数据失败: $e';
      print(_errorMessage);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // 加载上次选择的车辆
  Future<void> loadLastCar() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final lastCarIndex = prefs.getInt('lastCarIndex');
      
      if (lastCarIndex != null && lastCarIndex >= 0 && lastCarIndex < _cars.length) {
        _currentCar = _cars[lastCarIndex];
      } else if (_cars.isNotEmpty) {
        // 如果没有上次访问的记录，显示第一个车辆
        _currentCar = _cars[0];
        await saveLastCarIndex(0);
      }
      notifyListeners();
    } catch (e) {
      print('加载上次访问车辆失败: $e');
    }
  }

  // 保存上次选择的车辆索引
  Future<void> saveLastCarIndex(int index) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt('lastCarIndex', index);
    } catch (e) {
      print('保存上次选择的车辆索引失败: $e');
    }
  }

  // 设置当前车辆
  Future<void> setCurrentCar(Car car, int index) async {
    _currentCar = car;
    await saveLastCarIndex(index);
    notifyListeners();
  }

  // 搜索车辆
  List<Car> searchCars(String keyword) {
    return CarService.searchCars(_cars, keyword);
  }

  // 设置音频播放状态
  void setAudioPlayingState(bool isPlaying, String audioType) {
    _isPlayingAudio = isPlaying;
    _currentAudioType = audioType;
    notifyListeners();
  }

  // 重置音频播放状态
  void resetAudioState() {
    _isPlayingAudio = false;
    _currentAudioType = '';
    notifyListeners();
  }

  // 清除错误消息
  void clearError() {
    _errorMessage = '';
    notifyListeners();
  }
}