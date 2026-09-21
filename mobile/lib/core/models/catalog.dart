class Category {
  const Category({
    required this.id,
    required this.name,
    this.parentId,
    this.children = const [],
    this.productCount = 0,
  });

  final int id;
  final String name;
  final int? parentId;
  final List<Category> children;
  final int productCount;

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'] as int,
      name: json['name'] as String,
      parentId: json['parent_id'] as int?,
      productCount: json['product_count'] as int? ?? 0,
      children: (json['children'] as List? ?? const [])
          .map((e) => Category.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class SizeOption {
  const SizeOption({required this.id, required this.name});

  final int id;
  final String name;

  factory SizeOption.fromJson(Map<String, dynamic> json) {
    return SizeOption(
      id: json['id'] as int,
      name: json['name'] as String,
    );
  }
}

class ColorOption {
  const ColorOption({required this.id, required this.name, this.hex});

  final int id;
  final String name;
  final String? hex;

  factory ColorOption.fromJson(Map<String, dynamic> json) {
    return ColorOption(
      id: json['id'] as int,
      name: json['name'] as String,
      hex: json['hex'] as String?,
    );
  }
}

class ProductVariant {
  const ProductVariant({
    required this.id,
    required this.size,
    required this.color,
    this.stock = 0,
    this.price,
    this.images = const [],
  });

  final int id;
  final SizeOption size;
  final ColorOption color;
  final int stock;
  final double? price;
  final List<String> images;

  factory ProductVariant.fromJson(Map<String, dynamic> json) {
    final sizeRaw = json['size'] as Map<String, dynamic>? ?? const {};
    final colorRaw = json['color'] as Map<String, dynamic>? ?? const {};
    return ProductVariant(
      id: json['id'] as int,
      size: SizeOption(
        id: sizeRaw['id'] as int? ?? 0,
        name: sizeRaw['name'] as String? ?? '—',
      ),
      color: ColorOption(
        id: colorRaw['id'] as int? ?? 0,
        name: colorRaw['name'] as String? ?? '—',
        hex: colorRaw['hex'] as String?,
      ),
      stock: json['stock'] as int? ?? 0,
      price: (json['price'] as num?)?.toDouble(),
      images: (json['images'] as List? ?? const []).cast<String>(),
    );
  }

  bool get inStock => stock > 0;
}

class Product {
  const Product({
    required this.id,
    required this.name,
    required this.price,
    this.description,
    this.category,
    this.brand,
    this.images = const [],
    this.tags = const [],
    this.variants = const [],
    this.rating = 0,
    this.reviewCount = 0,
    this.discount = 0,
    this.isNew = false,
  });

  final int id;
  final String name;
  final double price;
  final String? description;
  final String? category;
  final String? brand;
  final List<String> images;
  final List<String> tags;
  final List<ProductVariant> variants;
  final double rating;
  final int reviewCount;
  final double discount;
  final bool isNew;

  bool get hasDiscount => discount > 0;
  double get finalPrice => hasDiscount ? price * (1 - discount / 100) : price;
  String get primaryImage => images.isNotEmpty ? images.first : '';

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as int,
      name: json['name'] as String,
      price: (json['price'] as num).toDouble(),
      description: json['description'] as String?,
      category: json['category'] as String?,
      brand: json['brand'] as String?,
      images: (json['images'] as List? ?? const []).cast<String>(),
      tags: (json['tags'] as List? ?? const []).cast<String>(),
      variants: (json['variants'] as List? ?? const [])
          .map((e) => ProductVariant.fromJson(e as Map<String, dynamic>))
          .toList(),
      rating: (json['rating'] as num?)?.toDouble() ?? 0,
      reviewCount: json['review_count'] as int? ?? 0,
      discount: (json['discount'] as num?)?.toDouble() ?? 0,
      isNew: json['is_new'] as bool? ?? false,
    );
  }
}

class CatalogPage {
  const CatalogPage({
    required this.items,
    required this.page,
    required this.totalPages,
    required this.total,
  });

  final List<Product> items;
  final int page;
  final int totalPages;
  final int total;

  factory CatalogPage.fromJson(Map<String, dynamic> json) {
    return CatalogPage(
      items: (json['items'] as List? ?? const [])
          .map((e) => Product.fromJson(e as Map<String, dynamic>))
          .toList(),
      page: json['page'] as int? ?? 0,
      totalPages: json['total_pages'] as int? ?? 1,
      total: json['total'] as int? ?? 0,
    );
  }
}