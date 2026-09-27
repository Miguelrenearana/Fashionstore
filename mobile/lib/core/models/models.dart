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
    this.available,
  });

  final int variantId;
  final int productId;
  final String name;
  final double price;
  final int quantity;
  final String? size;
  final String? color;
  final String? imageUrl;
  final int? available;

  double get subtotal => price * quantity;
  String get variantLabel =>
      [size, color].where((e) => e != null && e.isNotEmpty).join(' · ');

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
      available: available,
    );
  }

  /// Contrato de `GET /cart` (CU-20). El backend llama `unit_price`, `size_name`,
  /// `color_name` y `garment_name`; antes se leian `price`/`size`/`color`/`name`
  /// y el carrito aparecia vacio.
  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      variantId: json['variant_id'] as int,
      productId: json['garment_id'] as int? ?? json['product_id'] as int? ?? 0,
      name: json['garment_name'] as String? ??
          json['name'] as String? ??
          'Prenda #${json['variant_id']}',
      price: (json['unit_price'] as num? ?? json['price'] as num? ?? 0)
          .toDouble(),
      quantity: json['quantity'] as int? ?? 1,
      size: json['size_name'] as String? ?? json['size'] as String?,
      color: json['color_name'] as String? ?? json['color'] as String?,
      imageUrl: json['image_url'] as String?,
      available: json['available'] as int?,
    );
  }
}

class ProductRecommendation {
  const ProductRecommendation({
    required this.product,
    this.score = 0,
    this.reason,
    this.variantId,
    this.variantSku,
    this.sizeName,
    this.colorName,
  });

  final Product product;
  final double score;
  final String? reason;
  final int? variantId;
  final String? variantSku;
  final String? sizeName;
  final String? colorName;

  /// CU-30: `GET /ai/recommendations` devuelve una lista plana por variante, no
  /// un objeto con `product` anidado. Antes se leia `json['product']`, que
  /// siempre venía null y reventaba el parseo.
  factory ProductRecommendation.fromJson(Map<String, dynamic> json) {
    final nested = json['product'];
    if (nested is Map<String, dynamic>) {
      return ProductRecommendation(
        product: Product.fromJson(nested),
        score: (json['score'] as num?)?.toDouble() ?? 0,
        reason: json['reason'] as String?,
      );
    }
    final imageUrl = json['garment_image_url'] as String?;
    return ProductRecommendation(
      product: Product(
        // La recomendacion viene identificada por variante, que es lo unico que
        // permite abrir el detalle y elegir talla.
        id: (json['variant_id'] as num?)?.toInt() ?? 0,
        name: json['garment_name'] as String? ?? 'Prenda',
        price: (json['price'] as num?)?.toDouble() ?? 0,
        images: imageUrl != null && imageUrl.isNotEmpty ? [imageUrl] : const [],
      ),
      score: (json['score'] as num?)?.toDouble() ?? 0,
      variantId: (json['variant_id'] as num?)?.toInt(),
      variantSku: json['variant_sku'] as String?,
      sizeName: json['size_name'] as String?,
      colorName: json['color_name'] as String?,
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