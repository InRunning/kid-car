// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:kid_car_flutter/main.dart';

void main() {
  testWidgets('KidCarApp smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const KidCarApp());

    // Verify that our app title is displayed.
    expect(find.text('儿童认识车'), findsOneWidget);
    
    // Verify that bottom navigation items are present.
    expect(find.text('首页'), findsOneWidget);
    expect(find.text('搜索'), findsOneWidget);
  });
}
