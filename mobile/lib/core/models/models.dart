import '../models/catalog.dart' show Product;

class User {
  const User({
    required this.id,
    required this.email,
    required this.fullName,
    this.phone,
    this.avatarUrl,
    this.role = 'client',
    this.points = 0,
  });

  final int id;
  final String email;
  final String fullName;
  final String? phone;
  final String? avatarUrl;
  final String role;
  final int points;

  bool get isClient => role == 'client';
  bool get isAdmin => role == 'admin';

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      email: json['email'] as String,
      fullName: json['full_name'] as String? ?? json['name'] as String? ?? '',
      phone: json['phone'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      role: json['role'] as String? ?? 'client',
      points: json['points'] as int? ?? 0,
    );
  }
}

class AuthSession {
  const AuthSession({
    required this.accessToken,
    required this.user,
    this.refreshToken,
  });

  final String accessToken;
  final String? refreshToken;
  final User user;

  bool get isAuthenticated => accessToken.isNotEmpty;

  factory AuthSession.fromJson(Map<String, dynamic> json) {
    return AuthSession(
      accessToken: json['access_token'] as String? ?? '',
      refreshToken: json['refresh_token'] as String?,
      user: User.fromJson(json['user'] as Map<String, dynamic>),
    );
  }
}

class CartItem {
  const CartItem({
    required this.variantId,
    required this.productId,
    required this.name,
    required this.price,
    this.quantity = 1,
    this.size,
    this.color,
    this.imageUrl,
  });

  final int variantId;
  final int productId;
  final String name;
  final double price;
  final int quantity;
  final String? size;
  final String? color;
  final String? imageUrl;

  double get subtotal => price * quantity;

  CartItem copyWith({int? quantity}) {
    return CartItem(
      variantId: variantId,
      productId: productId,
      name: name,
      price: price,
      quantity: quantity ?? this.quantity,
      size: size,
      color: color,
      imageUrl: imageUrl,
    );
  }

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      variantId: json['variant_id'] as int,
      productId: json['product_id'] as int? ?? 0,
      name: json['name'] as String,
      price: (json['price'] as num).toDouble(),
      quantity: json['quantity'] as int? ?? 1,
      size: json['size'] as String?,
      color: json['color'] as String?,
      imageUrl: json['image_url'] as String?,
    );
  }
}

class ProductRecommendation {
  const ProductRecommendation({
    required this.product,
    this.score = 0,
    this.reason,
  });

  final Product product;
  final double score;
  final String? reason;

  factory ProductRecommendation.fromJson(Map<String, dynamic> json) {
    return ProductRecommendation(
      product: Product.fromJson(json['product'] as Map<String, dynamic>),
      score: (json['score'] as num?)?.toDouble() ?? 0,
      reason: json['reason'] as String?,
    );
  }
}

class NotificationItem {
  const NotificationItem({
    required this.id,
    required this.title,
    required this.body,
    required this.createdAt,
    this.read = false,
    this.type,
    this.deepLink,
  });

  final int id;
  final String title;
  final String body;
  final DateTime createdAt;
  final bool read;
  final String? type;
  final String? deepLink;

  factory NotificationItem.fromJson(Map<String, dynamic> json) {
    return NotificationItem(
      id: json['id'] as int,
      title: json['title'] as String,
      body: json['body'] as String,
      createdAt:
          DateTime.tryParse(json['created_at'] as String? ?? '') ?? DateTime.now(),
      read: json['is_read'] as bool? ?? json['read'] as bool? ?? false,
      type: json['type'] as String?,
      deepLink: json['deep_link'] as String?,
    );
  }
}