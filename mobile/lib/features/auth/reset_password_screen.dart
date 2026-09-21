import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/design/design.dart';
import '../../core/network/api_client.dart';
import '../../core/di/providers.dart';
import '../../shared/widgets/shared_widgets.dart';

class ResetPasswordScreen extends ConsumerStatefulWidget {
  const ResetPasswordScreen({super.key, this.token});

  final String? token;

  @override
  ConsumerState<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends ConsumerState<ResetPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _tokenController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmController = TextEditingController();
  bool _obscure = true;
  bool _loading = false;
  bool _done = false;

  @override
  void initState() {
    super.initState();
    if (widget.token != null) {
      _tokenController.text = widget.token!;
    }
  }

  @override
  void dispose() {
    _tokenController.dispose();
    _passwordController.dispose();
    _confirmController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      await ref.read(apiClientProvider).post('/auth/reset-password', data: {
        'token': _tokenController.text.trim(),
        'new_password': _passwordController.text,
      });
      if (mounted) setState(() => _done = true);
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
        title: const Text('Restablecer contraseña'),
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.x5),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: _done
                ? Column(
                    children: [
                      const AppEmptyState(
                        title: 'Contraseña actualizada',
                        message:
                            'Ya puedes iniciar sesión con tu nueva contraseña.',
                        icon: Icons.verified_outlined,
                      ),
                      AppButton(
                        label: 'Iniciar sesión',
                        onPressed: () => context.go('/auth/login'),
                      ),
                    ],
                  )
                : Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          'Crea tu nueva contraseña',
                          style: theme.textTheme.headlineMedium,
                        ),
                        const SizedBox(height: AppSpacing.x5),
                        AppTextField(
                          controller: _tokenController,
                          label: 'Código de verificación',
                          hintText: 'Ingresa el código recibido por correo',
                          prefixIcon: Icons.verified_user_outlined,
                          textInputAction: TextInputAction.next,
                          validator: (v) {
                            if (v == null || v.isEmpty) {
                              return 'Ingresa el código de verificación';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: AppSpacing.x4),
                        AppTextField(
                          controller: _passwordController,
                          label: 'Nueva contraseña',
                          prefixIcon: Icons.lock_outline,
                          obscureText: _obscure,
                          textInputAction: TextInputAction.next,
                          suffixIcon: IconButton(
                            onPressed: () => setState(() => _obscure = !_obscure),
                            icon: Icon(
                              _obscure ? Icons.visibility : Icons.visibility_off,
                              size: 20,
                            ),
                          ),
                          validator: (v) {
                            if (v == null || v.length < 8) {
                              return 'Mínimo 8 caracteres';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: AppSpacing.x4),
                        AppTextField(
                          controller: _confirmController,
                          label: 'Confirmar contraseña',
                          prefixIcon: Icons.lock_outline,
                          obscureText: _obscure,
                          textInputAction: TextInputAction.done,
                          onSubmitted: (_) => _submit(),
                          validator: (v) {
                            if (v != _passwordController.text) {
                              return 'Las contraseñas no coinciden';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: AppSpacing.x5),
                        AppButton(
                          label: 'Guardar contraseña',
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
}