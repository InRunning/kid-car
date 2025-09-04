import 'dart:convert';
import 'dart:io';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import '../models/car_model.dart';

class CarService {
  static const String _carJsonPath = 'assets/car.json';

  // 从assets加载车辆数据
  static Future<List<Car>> loadCarsFromAssets() async {
    try {
      // 从assets读取JSON文件
      final String jsonString = await rootBundle.loadString(_carJsonPath);
      final List<dynamic> jsonList = json.decode(jsonString);
      
      // 将JSON列表转换为Car对象列表
      return jsonList.map((json) => Car.fromJson(json)).toList();
    } catch (e) {
      print('加载车辆数据失败: $e');
      return [];
    }
  }

  // 从本地文件加载车辆数据（如果需要）
  static Future<List<Car>> loadCarsFromLocalFile() async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/car.json');
      
      if (await file.exists()) {
        final String jsonString = await file.readAsString();
        final List<dynamic> jsonList = json.decode(jsonString);
        return jsonList.map((json) => Car.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      print('从本地文件加载车辆数据失败: $e');
      return [];
    }
  }

  // 保存车辆数据到本地文件（如果需要）
  static Future<bool> saveCarsToLocalFile(List<Car> cars) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/car.json');
      
      final List<Map<String, dynamic>> jsonList = 
          cars.map((car) => car.toJson()).toList();
      final String jsonString = json.encode(jsonList);
      
      await file.writeAsString(jsonString);
      return true;
    } catch (e) {
      print('保存车辆数据到本地文件失败: $e');
      return false;
    }
  }

  // 搜索车辆
  static List<Car> searchCars(List<Car> cars, String keyword) {
    if (keyword.trim().isEmpty) {
      return cars;
    }
    
    final lowerKeyword = keyword.toLowerCase();
    return cars.where((car) {
      final chineseName = car.carName.toLowerCase();
      final englishName = car.carEnglishName.toLowerCase();
      final carType = car.carType.toLowerCase();
      
      return chineseName.contains(lowerKeyword) || 
             englishName.contains(lowerKeyword) ||
             carType.contains(lowerKeyword);
    }).toList();
  }
}