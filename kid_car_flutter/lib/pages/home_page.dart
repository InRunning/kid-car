import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:vibration/vibration.dart';
import '../providers/car_provider.dart';
import '../services/audio_service.dart';

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> with TickerProviderStateMixin {
  late AnimationController _animationController;
  late AnimationController _pulseController;
  late Animation<double> _rotationAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<double> _pulseAnimation;
  bool _isAnimating = false;
  final AudioService _audioService = AudioService.instance;

  @override
  void initState() {
    super.initState();
    
    // 主动画控制器 - 旋转和缩放
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    
    // 脉冲动画控制器 - 背景光晕效果
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    // 旋转动画 - 360度旋转
    _rotationAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));
    
    // 缩放动画 - 先放大再回到原始大小
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.3,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticInOut,
    ));
    
    // 脉冲动画 - 背景光晕效果
    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.5,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));
    
    // 加载车辆数据
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<CarProvider>(context, listen: false).loadCars();
    });
  }

  @override
  void dispose() {
    _animationController.dispose();
    _pulseController.dispose();
    // 不再释放音频服务，因为它是单例
    // _audioService.dispose();
    super.dispose();
  }

  // 震动效果
  Future<void> _vibrate() async {
    try {
      if (await Vibration.hasVibrator() == true) {
        Vibration.vibrate(duration: 200);
      }
    } catch (e) {
      print('震动失败: $e');
    }
  }

  // 酷炫的旋转放大效果
  void _performCoolAnimation() {
    setState(() {
      _isAnimating = true;
    });
    
    // 重置动画
    _animationController.reset();
    _pulseController.reset();
    
    // 启动脉冲背景效果
    _pulseController.repeat(reverse: true);
    
    // 启动主动画
    _animationController.forward();
    
    // 动画完成后重置状态
    Future.delayed(const Duration(milliseconds: 1200), () {
      if (mounted) {
        _pulseController.stop();
        _pulseController.reset();
        setState(() {
          _isAnimating = false;
        });
      }
    });
  }

  // 播放车辆音频
  Future<void> _playCarAudio(CarProvider carProvider) async {
    if (carProvider.currentCar == null || carProvider.isPlayingAudio || _isAnimating) return;
    
    // 震动效果
    await _vibrate();
    
    // 酷炫的旋转放大效果
    _performCoolAnimation();
    
    // 播放英文音频
    await _audioService.playCarAudio(
      car: carProvider.currentCar!,
      onStateChanged: (isPlaying, audioType) {
        carProvider.setAudioPlayingState(isPlaying, audioType);
      },
      onError: (error) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error)),
        );
        carProvider.resetAudioState();
      },
    );
  }


  @override
  Widget build(BuildContext context) {
    return Consumer<CarProvider>(
      builder: (context, carProvider, child) {
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
                  : _buildCarContent(carProvider),
        );
      },
    );
  }

  // 切换到上一个车辆
  void _previousCar(CarProvider carProvider) {
    if (carProvider.cars.isEmpty || carProvider.currentCar == null) return;
    
    final currentIndex = carProvider.cars.indexOf(carProvider.currentCar!);
    final previousIndex = currentIndex > 0 ? currentIndex - 1 : carProvider.cars.length - 1;
    
    carProvider.setCurrentCar(carProvider.cars[previousIndex], previousIndex);
  }

  // 切换到下一个车辆
  void _nextCar(CarProvider carProvider) {
    if (carProvider.cars.isEmpty || carProvider.currentCar == null) return;
    
    final currentIndex = carProvider.cars.indexOf(carProvider.currentCar!);
    final nextIndex = currentIndex < carProvider.cars.length - 1 ? currentIndex + 1 : 0;
    
    carProvider.setCurrentCar(carProvider.cars[nextIndex], nextIndex);
  }

  Widget _buildCarContent(CarProvider carProvider) {
    if (carProvider.currentCar == null) {
      return const Center(
        child: Text('请从搜索页面选择车辆'),
      );
    }

    return GestureDetector(
      onHorizontalDragEnd: (details) {
        // 检测滑动方向
        if (details.primaryVelocity! > 0) {
          // 向右滑动，显示上一个车辆
          _previousCar(carProvider);
        } else if (details.primaryVelocity! < 0) {
          // 向左滑动，显示下一个车辆
          _nextCar(carProvider);
        }
      },
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
          // 车辆图片
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  GestureDetector(
                    onTap: () => _playCarAudio(carProvider),
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        // 背景光晕效果
                        if (_isAnimating)
                          AnimatedBuilder(
                            animation: _pulseAnimation,
                            builder: (context, child) {
                              return Container(
                                width: 250 * _pulseAnimation.value,
                                height: 250 * _pulseAnimation.value,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  gradient: RadialGradient(
                                    colors: [
                                      Colors.green.withOpacity(0.3),
                                      Colors.green.withOpacity(0.1),
                                      Colors.transparent,
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
                        
                        // 主要的车辆图片动画
                        AnimatedBuilder(
                          animation: Listenable.merge([_rotationAnimation, _scaleAnimation]),
                          builder: (context, child) {
                            return Transform.scale(
                              scale: _isAnimating ? _scaleAnimation.value : 1.0,
                              child: Transform.rotate(
                                angle: _isAnimating ? _rotationAnimation.value * 2 * 3.14159 : 0.0,
                                child: Container(
                                  decoration: _isAnimating ? BoxDecoration(
                                    borderRadius: BorderRadius.circular(20),
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.green.withOpacity(0.5),
                                        blurRadius: 20,
                                        spreadRadius: 5,
                                      ),
                                    ],
                                  ) : null,
                                  child: Image.asset(
                                    carProvider.currentCar!.carImagePath,
                                    height: 200,
                                    fit: BoxFit.contain,
                                    errorBuilder: (context, error, stackTrace) {
                                      return const Icon(
                                        Icons.directions_car,
                                        size: 200,
                                        color: Colors.grey,
                                      );
                                    },
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                        
                        // 闪烁的星星效果
                        if (_isAnimating)
                          ...List.generate(6, (index) {
                            final angle = (index * 60) * 3.14159 / 180;
                            return AnimatedBuilder(
                              animation: _animationController,
                              builder: (context, child) {
                                final progress = _animationController.value;
                                final distance = 120 * progress;
                                return Transform.translate(
                                  offset: Offset(
                                    distance * math.cos(angle),
                                    distance * math.sin(angle),
                                  ),
                                  child: Transform.scale(
                                    scale: (1 - progress) * 2,
                                    child: Icon(
                                      Icons.star,
                                      color: Colors.yellow.withOpacity(1 - progress),
                                      size: 20,
                                    ),
                                  ),
                                );
                              },
                            );
                          }),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // 音频播放状态
                  if (carProvider.isPlayingAudio)
                    Text(
                      carProvider.currentAudioType.contains('english') 
                          ? '正在播放英文 (${carProvider.currentAudioType})...'
                          : carProvider.currentAudioType.contains('chinese')
                              ? '正在播放中文...'
                              : '正在播放音频...',
                      style: const TextStyle(
                        color: Colors.green,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // 车辆信息
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    carProvider.currentCar!.carName,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    carProvider.currentCar!.carEnglishName,
                    style: const TextStyle(
                      fontSize: 18,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    carProvider.currentCar!.carDescription,
                    style: const TextStyle(
                      fontSize: 16,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // 车辆导航指示器
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      IconButton(
                        onPressed: () => _previousCar(carProvider),
                        icon: const Icon(Icons.arrow_back_ios),
                        iconSize: 32,
                        color: Colors.green,
                      ),
                      Column(
                        children: [
                          Text(
                            '${carProvider.cars.indexOf(carProvider.currentCar!) + 1} / ${carProvider.cars.length}',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Row(
                            mainAxisSize: MainAxisSize.min,
                            children: List.generate(
                              carProvider.cars.length,
                              (index) => Container(
                                margin: const EdgeInsets.symmetric(horizontal: 2),
                                width: 8,
                                height: 8,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: index == carProvider.cars.indexOf(carProvider.currentCar!)
                                      ? Colors.green
                                      : Colors.grey.shade300,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                      IconButton(
                        onPressed: () => _nextCar(carProvider),
                        icon: const Icon(Icons.arrow_forward_ios),
                        iconSize: 32,
                        color: Colors.green,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // 操作说明
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Padding(
              padding: EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '操作说明',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    '• 点击车辆图片：震动 + 酷炫旋转放大效果并播放英文音频\n• 左右滑动屏幕：切换不同车辆\n• 点击箭头按钮：切换车辆',
                    style: TextStyle(
                      fontSize: 16,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
          ),
          ],
        ),
      ),
    );
  }
}