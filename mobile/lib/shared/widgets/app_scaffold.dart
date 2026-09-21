import 'package:flutter/material.dart';

import 'app_bottom_nav.dart';

class AppScaffold extends StatelessWidget {
  const AppScaffold({
    super.key,
    required this.child,
    this.appBar,
    this.bottomNav,
    this.drawer,
    this.floatingActionButton,
    this.padding,
  });

  final Widget child;
  final AppBar? appBar;
  final AppBottomNav? bottomNav;
  final Widget? drawer;
  final Widget? floatingActionButton;
  final EdgeInsetsGeometry? padding;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: appBar,
      body: SafeArea(
        child: padding != null
            ? Padding(padding: padding!, child: child)
            : child,
      ),
      bottomNavigationBar: bottomNav,
      drawer: drawer,
      floatingActionButton: floatingActionButton,
    );
  }
}