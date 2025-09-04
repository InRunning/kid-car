import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/car_model.dart';
import '../providers/car_provider.dart';

class SearchPage extends StatefulWidget {
  final VoidCallback? onCarSelected;
  
  const SearchPage({Key? key, this.onCarSelected}) : super(key: key);

  @override
  _SearchPageState createState() => _SearchPageState();
}

class _SearchPageState extends State<SearchPage> {
  final TextEditingController _searchController = TextEditingController();
  List<Car> _filteredCars = [];
  Map<String, List<Car>> _groupedCars = {};
  String _searchKeyword = '';
  bool _showGrouped = true;

  @override
  void initState() {
    super.initState();
    _searchController.addListener(_onSearchChanged);
    
    // 加载车辆数据
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final carProvider = Provider.of<CarProvider>(context, listen: false);
      if (carProvider.cars.isEmpty) {
        carProvider.loadCars();
      } else {
        _filteredCars = carProvider.cars;
      }
    });
  }

  @override
  void dispose() {
    _searchController.removeListener(_onSearchChanged);
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged() {
    final carProvider = Provider.of<CarProvider>(context, listen: false);
    setState(() {
      _searchKeyword = _searchController.text;
      _filteredCars = carProvider.searchCars(_searchKeyword);
      
      // 如果有搜索关键词，显示列表模式；否则显示分组模式
      _showGrouped = _searchKeyword.trim().isEmpty;
      
      if (_showGrouped) {
        _groupedCars = _groupCarsByType(carProvider.cars);
      }
    });
  }
  
  // 按车辆类型分组
  Map<String, List<Car>> _groupCarsByType(List<Car> cars) {
    Map<String, List<Car>> grouped = {};
    for (Car car in cars) {
      if (!grouped.containsKey(car.carType)) {
        grouped[car.carType] = [];
      }
      grouped[car.carType]!.add(car);
    }
    return grouped;
  }

  Future<void> _selectCar(Car car, int index) async {
    final carProvider = Provider.of<CarProvider>(context, listen: false);
    
    // 保存选中的车辆
    await carProvider.setCurrentCar(car, index);
    
    // 显示选择成功提示
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('已选择: ${car.carName}'),
        backgroundColor: Colors.green,
        duration: const Duration(milliseconds: 1000),
      ),
    );
    
    // 延迟切换到首页标签
    Future.delayed(const Duration(milliseconds: 1000), () {
      if (mounted && widget.onCarSelected != null) {
        widget.onCarSelected!();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<CarProvider>(
      builder: (context, carProvider, child) {
        // 初始化数据
        if (_searchKeyword.isEmpty && carProvider.cars.isNotEmpty) {
          if (_filteredCars.isEmpty) {
            _filteredCars = carProvider.cars;
          }
          if (_groupedCars.isEmpty) {
            _groupedCars = _groupCarsByType(carProvider.cars);
          }
        }
        
        return Scaffold(
          body: carProvider.isLoading
              ? const Center(child: CircularProgressIndicator())
              : carProvider.errorMessage.isNotEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(carProvider.errorMessage),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: () {
                              carProvider.clearError();
                              carProvider.loadCars();
                            },
                            child: const Text('重试'),
                          ),
                        ],
                      ),
                    )
                  : _buildSearchContent(carProvider),
        );
      },
    );
  }

  Widget _buildSearchContent(CarProvider carProvider) {
    return Column(
      children: [
        // 搜索框
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Card(
            elevation: 4,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Row(
                children: [
                  const Icon(Icons.search, color: Colors.grey),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      controller: _searchController,
                      decoration: const InputDecoration(
                        hintText: '搜索车辆名称或类型',
                        border: InputBorder.none,
                      ),
                    ),
                  ),
                  if (_searchKeyword.isNotEmpty)
                    IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        _searchController.clear();
                      },
                    ),
                ],
              ),
            ),
          ),
        ),
        
        // 车辆内容区域
        Expanded(
          child: _showGrouped ? _buildGroupedCarList(carProvider) : _buildSearchResultList(carProvider),
        ),
      ],
    );
  }

  // 构建分组车辆列表
  Widget _buildGroupedCarList(CarProvider carProvider) {
    if (_groupedCars.isEmpty) {
      return const Center(
        child: Text(
          '暂无车辆数据',
          style: TextStyle(
            fontSize: 16,
            color: Colors.grey,
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      itemCount: _groupedCars.keys.length,
      itemBuilder: (context, index) {
        final carType = _groupedCars.keys.elementAt(index);
        final carsInType = _groupedCars[carType]!;
        
        return Card(
          elevation: 2,
          margin: const EdgeInsets.only(bottom: 12.0),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: ExpansionTile(
            title: Text(
              carType,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.green,
              ),
            ),
            subtitle: Text(
              '${carsInType.length} 种车辆',
              style: const TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
            ),
            children: carsInType.map((car) {
              final originalIndex = carProvider.cars.indexOf(car);
              return ListTile(
                onTap: () => _selectCar(car, originalIndex),
                title: Text(
                  car.carName,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                subtitle: Text(
                  car.carEnglishName,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Colors.grey,
                  ),
                ),
                trailing: const Icon(
                  Icons.arrow_forward_ios,
                  color: Colors.grey,
                  size: 16,
                ),
              );
            }).toList(),
          ),
        );
      },
    );
  }

  // 构建搜索结果列表
  Widget _buildSearchResultList(CarProvider carProvider) {
    if (_filteredCars.isEmpty) {
      return const Center(
        child: Text(
          '没有找到相关车辆',
          style: TextStyle(
            fontSize: 16,
            color: Colors.grey,
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      itemCount: _filteredCars.length,
      itemBuilder: (context, index) {
        final car = _filteredCars[index];
        final originalIndex = carProvider.cars.indexOf(car);
        
        return Card(
          elevation: 2,
          margin: const EdgeInsets.only(bottom: 8.0),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          child: ListTile(
            onTap: () => _selectCar(car, originalIndex),
            title: Text(
              car.carName,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  car.carEnglishName,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '类型: ${car.carType}',
                  style: const TextStyle(
                    fontSize: 12,
                    color: Colors.green,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
            trailing: const Icon(
              Icons.arrow_forward_ios,
              color: Colors.grey,
            ),
          ),
        );
      },
    );
  }
}