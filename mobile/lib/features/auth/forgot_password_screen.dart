import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/design/design.dart';
import '../../core/network/api_client.dart';
import '../../core/di/providers.dart';
import '../../shared/widgets/shared_widgets.dart';

class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  bool _loading = false;
  bool _sent = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      await ref.read(apiClientProvider).post('/auth/forgot-password', data: {
        'email': _emailController.text.trim(),
      });
      if (mounted) setState(() => _sent = true);
    } on ApiException catch (e) {
      if (mounted) {
        AppToast.show(context, message: e.message, type: ToastType.error);
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        foregroundColor: AppColors.textMain,
        elevation: 0,
        title: const Text('Recuperar contraseña'),
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.x5),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: _sent
                ? _buildSuccess(theme)
                : Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Container(
                          width: 64,
                          height: 64,
                          decoration: const BoxDecoration(
                            color: AppColors.primaryLight,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.lock_reset,
                            color: AppColors.primaryDark,
                            size: 32,
                          ),
                        ),
                        const SizedBox(height: AppSpacing.x4),
                        Text(
                          '¿Olvidaste tu contraseña?',
                          textAlign: TextAlign.center,
                          style: theme.textTheme.headlineMedium,
                        ),
                        const SizedBox(height: AppSpacing.x2),
                        Text(
                          'Ingresa tu correo y te enviaremos un enlace para restablecerla.',
                          textAlign: TextAlign.center,
                          style: theme.textTheme.bodyMedium
                              ?.copyWith(color: AppColors.textSecondary),
                        ),
                        const SizedBox(height: AppSpacing.x6),
                        AppTextField(
                          controller: _emailController,
                          label: 'Correo electrónico',
                          prefixIcon: Icons.email_outlined,
                          keyboardType: TextInputType.emailAddress,
                          textInputAction: TextInputAction.done,
                          onSubmitted: (_) => _submit(),
                          validator: (v) {
                            if (v == null || v.isEmpty) return 'Ingresa tu correo';
                            return null;
                          },
                        ),
                        const SizedBox(height: AppSpacing.x5),
                        AppButton(
                          label: 'Enviar enlace',
                          loading: _loading,
                          size: AppButtonSize.lg,
                          onPressed: _submit,
                        ),
                      ],
                    ),
                  ),
          ),
        ),
      ),
    );
  }

  Widget _buildSuccess(ThemeData theme) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const AppEmptyState(
          title: 'Revisa tu correo',
          message:
              'Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.',
          icon: Icons.mark_email_read_outlined,
        ),
        AppButton(
          label: 'Volver a iniciar sesión',
          variant: AppButtonVariant.secondary,
          onPressed: () => context.go('/auth/login'),
        ),
      ],
    );
  }
}