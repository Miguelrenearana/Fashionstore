import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/design/design.dart';
import '../../core/network/api_client.dart';
import '../../core/di/providers.dart';
import '../../shared/widgets/shared_widgets.dart';

class ChatMessage {
  const ChatMessage({
    required this.text,
    required this.isUser,
    this.isTyping = false,
  });

  final String text;
  final bool isUser;
  final bool isTyping;
}

class ChatState {
  const ChatState({this.messages = const [], this.isLoading = false});

  final List<ChatMessage> messages;
  final bool isLoading;
}

class ChatController extends StateNotifier<ChatState> {
  ChatController(this._api)
      : super(const ChatState(messages: [
          ChatMessage(
            text:
                '¡Hola! Soy la asistente de FashionStore. Pregúntame sobre prendas, tallas, disponibilidad o tendencias.',
            isUser: false,
          ),
        ]));

  final ApiClient _api;

  Future<void> send(String text) async {
    state = ChatState(
      messages: [
        ...state.messages,
        ChatMessage(text: text, isUser: true),
        const ChatMessage(text: '', isUser: false, isTyping: true),
      ],
      isLoading: true,
    );
    try {
      final res = await _api.post('/ai/chat', data: {
        'message': text,
        'history': state.messages
            .where((m) => !m.isTyping)
            .map((m) => {'role': m.isUser ? 'user' : 'assistant', 'content': m.text})
            .toList(),
      });
      final reply = (res['reply'] ?? res['response'] ?? '') as String;
      state = ChatState(
        messages: [
          ...state.messages.where((m) => !m.isTyping),
          ChatMessage(text: reply.isEmpty ? 'No tengo respuesta aún.' : reply, isUser: false),
        ],
        isLoading: false,
      );
    } on ApiException catch (e) {
      state = ChatState(
        messages: [
          ...state.messages.where((m) => !m.isTyping),
          ChatMessage(text: 'Lo siento, hubo un error: ${e.message}', isUser: false),
        ],
        isLoading: false,
      );
    }
  }
}

final chatControllerProvider =
    StateNotifierProvider<ChatController, ChatState>((ref) {
  return ChatController(ref.watch(apiClientProvider));
});

class AIChatScreen extends ConsumerStatefulWidget {
  const AIChatScreen({super.key});

  @override
  ConsumerState<AIChatScreen> createState() => _AIChatScreenState();
}

class _AIChatScreenState extends ConsumerState<AIChatScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _send() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    _controller.clear();
    ref.read(chatControllerProvider.notifier).send(text);
    _scrollToBottom();
  }

  void _scrollToBottom([_]) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(chatControllerProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.navBg,
        foregroundColor: Colors.white,
        title: const Row(
          children: [
            CircleAvatar(
              radius: 16,
              backgroundColor: AppColors.primaryLight,
              child: Icon(Icons.smart_toy, size: 20, color: AppColors.primaryDark),
            ),
            SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Asistente FashionStore',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                Text('IA · Recomendaciones y dudas',
                    style: TextStyle(fontSize: 11, color: AppColors.navMuted)),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(AppSpacing.x4),
              itemCount: state.messages.length,
              itemBuilder: (context, index) {
                final message = state.messages[index];
                if (message.isTyping) {
                  return const _TypingBubble();
                }
                return _ChatBubble(message: message);
              },
            ),
          ),
          SafeArea(
            top: false,
            child: Container(
              padding: const EdgeInsets.all(AppSpacing.x3),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                boxShadow: AppShadows.md,
              ),
              child: Row(
                children: [
                  Expanded(
                    child: AppTextField(
                      controller: _controller,
                      hintText: 'Escribe tu mensaje…',
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _send(),
                      onChanged: _scrollToBottom,
                    ),
                  ),
                  const SizedBox(width: AppSpacing.x2),
                  IconButton.filled(
                    onPressed: _send,
                    style: IconButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                    ),
                    icon: const Icon(Icons.send),
                    tooltip: 'Enviar',
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  const _ChatBubble({required this.message});

  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isUser = message.isUser;

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: AppSpacing.x3),
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.x4,
          vertical: AppSpacing.x3,
        ),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.78,
        ),
        decoration: BoxDecoration(
          color: isUser
              ? AppColors.primary
              : Theme.of(context).colorScheme.surface,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(AppRadius.lg),
            topRight: const Radius.circular(AppRadius.lg),
            bottomLeft: Radius.circular(isUser ? AppRadius.lg : AppRadius.sm),
            bottomRight: Radius.circular(isUser ? AppRadius.sm : AppRadius.lg),
          ),
          border: isUser
              ? null
              : Border.all(
                  color: theme.brightness == Brightness.dark
                      ? AppColors.darkBorder
                      : AppColors.border,
                ),
        ),
        child: Text(
          message.text,
          style: theme.textTheme.bodyMedium?.copyWith(
            color: isUser ? Colors.white : null,
            height: 1.45,
          ),
        ),
      ),
    );
  }
}

class _TypingBubble extends StatefulWidget {
  const _TypingBubble();

  @override
  State<_TypingBubble> createState() => _TypingBubbleState();
}

class _TypingBubbleState extends State<_TypingBubble>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1000),
  )..repeat();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: AppSpacing.x3),
        padding: const EdgeInsets.all(AppSpacing.x4),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(AppRadius.lg),
            topRight: Radius.circular(AppRadius.lg),
            bottomRight: Radius.circular(AppRadius.lg),
            bottomLeft: Radius.circular(AppRadius.sm),
          ),
          border: Border.all(color: AppColors.border),
        ),
        child: AnimatedBuilder(
          animation: _controller,
          builder: (_, __) {
            final value = _controller.value;
            final activeDot = (value * 3).floor() % 3;
            return Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (i) {
                final opacity = i == activeDot ? 1.0 : 0.3;
                return Container(
                  margin: const EdgeInsets.only(right: 5),
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: AppColors.textMuted.withValues(alpha: opacity),
                    shape: BoxShape.circle,
                  ),
                );
              }),
            );
          },
        ),
      ),
    );
  }
}