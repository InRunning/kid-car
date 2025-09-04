import 'package:audioplayers/audioplayers.dart';
import '../models/car_model.dart';

class AudioService {
  static final AudioService _instance = AudioService._internal();
  static AudioService get instance => _instance;

  AudioService._internal();

  AudioPlayer _audioPlayer = AudioPlayer();
  bool _isPlaying = false;
  bool _shouldStop = false; // 添加全局停止标志

  // 获取新的音频播放器实例
  void _recreatePlayer() {
    _audioPlayer.dispose();
    _audioPlayer = AudioPlayer();
  }

  // 播放车辆音频（英文3次 + 中文1次）
  Future<void> playCarAudio({
    required Car car,
    required Function(bool, String) onStateChanged,
    required Function(String) onError,
  }) async {
    try {
      // 重置停止标志
      _shouldStop = false;

      // 播放英文音频3次
      int englishPlays = 0;
      while (englishPlays < 3 && !_shouldStop) {
        onStateChanged(true, 'english ${englishPlays + 1}/3');
        bool playSuccess = await _playAudio(
          audioPath: car.englishAudioPath,
          audioType: 'english ${englishPlays + 1}/3',
          onStateChanged: onStateChanged,
          onError: onError,
          recreatePlayer: englishPlays == 0, // 只在第一次播放时重新创建播放器
        );

        // 检查是否需要停止
        if (_shouldStop) {
          onStateChanged(false, '');
          return;
        }

        if (playSuccess) {
          englishPlays++;
          // 等待播放完成
          await _waitForPlaybackComplete();

          // 再次检查是否需要停止
          if (_shouldStop) {
            onStateChanged(false, '');
            return;
          }

          // 短暂间隔
          if (englishPlays < 3) {
            await Future.delayed(const Duration(milliseconds: 200));
            // 间隔后再次检查是否需要停止
            if (_shouldStop) {
              onStateChanged(false, '');
              return;
            }
          }
        } else {
          // 播放失败，跳过剩余次数
          break;
        }
      }

      // 检查是否需要停止
      if (_shouldStop) {
        onStateChanged(false, '');
        return;
      }

      // 短暂间隔后播放中文音频
      await Future.delayed(const Duration(milliseconds: 300));

      // 再次检查是否需要停止
      if (_shouldStop) {
        onStateChanged(false, '');
        return;
      }

      // 播放中文音频1次
      onStateChanged(true, 'chinese');
      await _playAudio(
        audioPath: car.chineseAudioPath,
        audioType: 'chinese',
        onStateChanged: onStateChanged,
        onError: onError,
        recreatePlayer: true,
      );

      // 检查是否需要停止
      if (_shouldStop) {
        onStateChanged(false, '');
        return;
      }

      // 等待播放完成
      await _waitForPlaybackComplete();

      // 重置状态
      onStateChanged(false, '');
    } catch (e) {
      onError('播放音频失败: $e');
      onStateChanged(false, '');
      return;
    }
  }

  // 播放一次英文音频
  Future<void> playEnglishAudioOnce({
    required Car car,
    required Function(bool, String) onStateChanged,
    required Function(String) onError,
  }) async {
    try {
      // 重置停止标志
      _shouldStop = false;

      onStateChanged(true, 'english');

      bool playSuccess = await _playAudio(
        audioPath: car.englishAudioPath,
        audioType: 'english',
        onStateChanged: onStateChanged,
        onError: onError,
        recreatePlayer: true,
      );

      // 检查是否需要停止
      if (_shouldStop) {
        onStateChanged(false, '');
        return;
      }

      if (playSuccess) {
        // 等待播放完成
        await _waitForPlaybackComplete();
      }

      // 重置状态
      onStateChanged(false, '');
    } catch (e) {
      onError('播放音频失败: $e');
      onStateChanged(false, '');
      return;
    }
  }

  // 等待播放完成
  Future<void> _waitForPlaybackComplete() async {
    while (_isPlaying && !_shouldStop) {
      await Future.delayed(const Duration(milliseconds: 100));
    }
  }

  // 播放单个音频
  Future<bool> _playAudio({
    required String audioPath,
    required String audioType,
    required Function(bool, String) onStateChanged,
    required Function(String) onError,
    bool recreatePlayer = true,
  }) async {
    try {
      print('尝试播放音频: $audioPath, 类型: $audioType');

      // 如果正在播放，先停止
      if (_isPlaying) {
        await _audioPlayer.stop();
        _isPlaying = false;
      }

      // 设置音频播放状态
      _isPlaying = true;
      onStateChanged(true, audioType);

      // 重新创建播放器实例以确保状态正确（仅在播放英文音频时）
      if (recreatePlayer) {
        _recreatePlayer();
      }

      // 设置音频完成回调
      _audioPlayer.onPlayerComplete.listen((_) {
        print('音频播放完成: $audioType');
        // 音频播放完毕，重置状态
        _isPlaying = false;
      });

      // 设置音频错误回调
      _audioPlayer.onPlayerStateChanged.listen((state) {
        print('音频播放状态变化: $state');
        if (state == PlayerState.stopped && _isPlaying) {
          // 播放停止可能是由于错误
          _isPlaying = false;
        } else if (state == PlayerState.completed) {
          // 播放完成
          _isPlaying = false;
        }
      });

      // 设置音量为最大
      await _audioPlayer.setVolume(1.0);
      
      // 播放音频 - 尝试使用不同的方式
      try {
        // 方法1: 使用AssetSource，需要移除assets/前缀，因为AssetSource会自动添加
        String assetPath =
            audioPath.startsWith('assets/')
                ? audioPath.substring(7)
                : audioPath;
        await _audioPlayer.play(AssetSource(assetPath));
        print('使用AssetSource播放音频成功');
        return true;
      } catch (e1) {
        print('AssetSource播放失败: $e1');
        try {
          // 方法2: 使用直接路径
          await _audioPlayer.play(DeviceFileSource(audioPath));
          print('使用DeviceFileSource播放音频成功');
          return true;
        } catch (e2) {
          print('DeviceFileSource播放失败: $e2');
          try {
            // 方法3: 使用URL
            await _audioPlayer.play(UrlSource(audioPath));
            print('使用UrlSource播放音频成功');
            return true;
          } catch (e3) {
            print('所有播放方式都失败: $e3');
            throw e3;
          }
        }
      }
    } catch (e) {
      print('音频播放异常: $e');
      _isPlaying = false;
      // 在Web平台上，音频播放可能会失败，但我们不希望这影响用户体验
      // 模拟音频播放完成
      await Future.delayed(const Duration(seconds: 1));
      // 显示错误
      onError('播放音频失败: $e');
      return false;
    }
  }

  // 停止播放
  Future<void> stop({Function(bool, String)? onStateChanged}) async {
    try {
      // 设置停止标志，中断正在进行的播放流程
      _shouldStop = true;

      // 停止音频播放器
      await _audioPlayer.stop();
      _isPlaying = false; // 重置播放状态

      // 通知状态变化
      if (onStateChanged != null) {
        onStateChanged(false, '');
      }

      print('音频播放已停止');
    } catch (e) {
      print('停止音频播放失败: $e');
      // 即使停止失败，也要设置停止标志和重置状态
      _shouldStop = true;
      _isPlaying = false;
      if (onStateChanged != null) {
        onStateChanged(false, '');
      }
    }
  }

  // 暂停播放
  Future<void> pause() async {
    try {
      await _audioPlayer.pause();
    } catch (e) {
      print('暂停音频播放失败: $e');
    }
  }

  // 恢复播放
  Future<void> resume() async {
    try {
      await _audioPlayer.resume();
    } catch (e) {
      print('恢复音频播放失败: $e');
    }
  }

  // 释放资源
  void dispose() {
    try {
      // 设置停止标志
      _shouldStop = true;
      _isPlaying = false;

      _audioPlayer.dispose();
    } catch (e) {
      print('释放音频播放器失败: $e');
    }
  }
}
