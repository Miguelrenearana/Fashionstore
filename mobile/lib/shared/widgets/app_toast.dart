import 'package:flutter/material.dart';

import '../../core/design/design.dart';

enum ToastType { success, error, info, warning }

class AppToast {
  static OverlayEntry? _current;

  static void show(
    BuildContext context, {
    required String message,
    ToastType type = ToastType.info,
    String? actionLabel,
    VoidCallback? onAction,
  }) {
    final overlay = Overlay.of(context);
    _current?.remove();

    final (bg, icon, fg) = switch (type) {
      ToastType.success => (AppColors.success, Icons.check_circle, Colors.white),
      ToastType.error => (AppColors.error, Icons.error, Colors.white),
      ToastType.warning => (AppColors.warning, Icons.warning_amber, Colors.white),
      ToastType.info => (AppColors.navBg, Icons.info, Colors.white),
    };

    _current = OverlayEntry(
      builder: (context) => _ToastWidget(
        message: message,
        bg: bg,
        icon: icon,
        fg: fg,
        actionLabel: actionLabel,
        onAction: onAction,
        onDismiss: () => _current = null,
      ),
    );

    overlay.insert(_current!);
    Future.delayed(const Duration(seconds: 4), () {
      _current?.remove();
      _current = null;
    });
  }
}

class _ToastWidget extends StatefulWidget {
  const _ToastWidget({
    required this.message,
    required this.bg,
    required this.icon,
    required this.fg,
    this.actionLabel,
    this.onAction,
    this.onDismiss,
  });

  final String message;
  final Color bg;
  final IconData icon;
  final Color fg;
  final String? actionLabel;
  final VoidCallback? onAction;
  final VoidCallback? onDismiss;

  @override
  State<_ToastWidget> createState() => _ToastWidgetState();
}

class _ToastWidgetState extends State<_ToastWidget>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 250),
  )..forward();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Align(
        alignment: Alignment.topCenter,
        child: FadeTransition(
          opacity: _controller,
          child: SlideTransition(
            position: Tween<Offset>(
              begin: const Offset(0, -1),
              end: Offset.zero,
            ).animate(CurvedAnimation(
              parent: _controller,
              curve: Curves.easeOutCubic,
            )),
            child: Material(
              color: Colors.transparent,
              child: Container(
                margin: const EdgeInsets.all(AppSpacing.x4),
                padding: const EdgeInsets.all(AppSpacing.x3),
                decoration: BoxDecoration(
                  color: widget.bg,
                  borderRadius: BorderRadius.circular(AppRadius.md),
                  boxShadow: AppShadows.lg,
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(widget.icon, color: widget.fg, size: 20),
                    const SizedBox(width: AppSpacing.x2),
                    Flexible(
                      child: Text(
                        widget.message,
                        style: Theme.of(context)
                            .textTheme
                            .bodyMedium
                            ?.copyWith(color: widget.fg),
                      ),
                    ),
                    if (widget.actionLabel != null) ...[
                      const SizedBox(width: AppSpacing.x2),
                      TextButton(
                        onPressed: widget.onAction,
                        style: TextButton.styleFrom(
                          foregroundColor: widget.fg,
                          minimumSize: const Size(0, 32),
                          padding: const EdgeInsets.symmetric(
                            horizontal: AppSpacing.x2,
                          ),
                        ),
                        child: Text(
                          widget.actionLabel!,
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                      ),
                    ],
                    const SizedBox(width: AppSpacing.x1),
                    InkWell(
                      onTap: () {
                        widget.onDismiss?.call();
                        // ignore: deprecated_member_use
                        Navigator.maybePop(context);
                      },
                      child: Padding(
                        padding: const EdgeInsets.all(2),
                        child: Icon(Icons.close, color: widget.fg, size: 16),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}