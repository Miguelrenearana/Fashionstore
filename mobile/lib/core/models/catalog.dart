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
    this.available = 0,
    this.price,
    this.images = const [],
  });

  final int id;
  final SizeOption size;
  final ColorOption color;

  /// Unidades fisicas en inventario.
  final int stock;

  /// Units available after subtracting reservations (CU-14).
  final int available;
  final double? price;
  final List<String> images;

  factory ProductVariant.fromJson(Map<String, dynamic> json) {
    // Handle both formats:
    // 1. Backend catalog list: {size: {name}, color: {name}, price, stock, available}
    // 2. Detail endpoint: {size: {id, name}, color: {id, name, hex}}
    final sizeRaw = json['size'];
    final colorRaw = json['color'];

    String sizeName = '—';
    String colorName = '—';
    String? colorHex;

    if (sizeRaw is Map) {
      sizeName = (sizeRaw['name'] ?? sizeRaw['size_name'] ?? '—') as String;
    } else if (sizeRaw is String) {
      sizeName = sizeRaw;
    }

    if (colorRaw is Map) {
      colorName =
          (colorRaw['name'] ?? colorRaw['color_name'] ?? '—') as String;
      colorHex = colorRaw['hex'] as String?;
    } else if (colorRaw is String) {
      colorName = colorRaw;
    }

    final stock = (json['stock'] as num?)?.toInt() ?? 0;
    final available =
        (json['available'] as num?)?.toInt() ?? stock;

    return ProductVariant(
      id: json['id'] as int,
      size: SizeOption(id: 0, name: sizeName),
      color: ColorOption(id: 0, name: colorName, hex: colorHex),
      stock: stock,
      available: available,
      price: (json['price'] as num?)?.toDouble(),
      images: (json['images'] as List? ?? const []).cast<String>(),
    );
  }

  bool get inStock => available > 0;
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
    // Backend format:
    // {
    //   id, name, description, base_price, min_price, in_stock, is_ar_enabled,
    //   category: {id, name, ...},
    //   images: [{id, url, is_primary}],
    //   variants: [{id, sku, price, size_name, color_name}]
    // }
    final List<String> imageUrls = (json['images'] as List? ?? const [])
        .where((img) => img is Map && img['url'] != null)
        .map((img) => img['url'] as String)
        .toList();

    final List<ProductVariant> variants = (json['variants'] as List? ?? const [])
        .map((v) => ProductVariant.fromJson({
              'id': v['id'],
              'size': {'id': 0, 'name': v['size_name'] ?? '—'},
              'color': {'id': 0, 'name': v['color_name'] ?? '—', 'hex': null},
              'stock': (v['stock'] as num?)?.toInt() ?? 0,
              'available': (v['available'] as num?)?.toInt() ?? 0,
              'price': (v['price'] as num?)?.toDouble(),
              'images': <String>[],
            }))
        .toList();

    return Product(
      id: json['id'] as int,
      name: json['name'] as String,
      price: ((json['min_price'] ?? json['base_price'] ?? 0) as num).toDouble(),
      description: json['description'] as String?,
      category: (json['category'] as Map?)?['name'] as String?,
      brand: null,
      images: imageUrls,
      tags: const [],
      variants: variants,
      rating: 0,
      reviewCount: 0,
      discount: 0,
      isNew: false,
    );
  }
}

class BranchStock {
  const BranchStock({
    required this.branchId,
    this.branchName,
    this.quantity = 0,
    this.reserved = 0,
    this.available = 0,
  });

  final int branchId;
  final String? branchName;
  final int quantity;
  final int reserved;
  final int available;

  factory BranchStock.fromJson(Map<String, dynamic> json) {
    return BranchStock(
      branchId: (json['branch_id'] as num).toInt(),
      branchName: json['branch_name'] as String?,
      quantity: (json['quantity'] as num?)?.toInt() ?? 0,
      reserved: (json['reserved_quantity'] as num?)?.toInt() ?? 0,
      available: (json['available'] as num?)?.toInt() ?? 0,
    );
  }
}

/// CU-14: disponibilidad de una variante desglosada por sucursal.
class VariantAvailability {
  const VariantAvailability({
    required this.variantId,
    required this.sku,
    required this.price,
    this.sizeName,
    this.colorName,
    this.totalAvailable = 0,
    this.branches = const [],
  });

  final int variantId;
  final String sku;
  final double price;
  final String? sizeName;
  final String? colorName;
  final int totalAvailable;
  final List<BranchStock> branches;

  factory VariantAvailability.fromJson(Map<String, dynamic> json) {
    return VariantAvailability(
      variantId: (json['variant_id'] as num).toInt(),
      sku: json['sku'] as String? ?? '',
      price: (json['price'] as num?)?.toDouble() ?? 0,
      sizeName: json['size_name'] as String?,
      colorName: json['color_name'] as String?,
      totalAvailable: (json['total_available'] as num?)?.toInt() ?? 0,
      branches: (json['branches'] as List? ?? const [])
          .map((e) => BranchStock.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  int availableAt(int? branchId) {
    if (branchId == null) return totalAvailable;
    return branches
        .firstWhere(
          (b) => b.branchId == branchId,
          orElse: () => BranchStock(branchId: branchId),
        )
        .available;
  }
}

/// CU-14: sucursal selectable para consultar disponibilidad.
class Branch {
  const Branch({
    required this.id,
    required this.name,
    this.cityName,
  });

  final int id;
  final String name;
  final String? cityName;

  factory Branch.fromJson(Map<String, dynamic> json) {
    final city = json['city'];
    return Branch(
      id: (json['id'] as num).toInt(),
      name: json['name'] as String? ?? '',
      cityName: city is Map ? city['name'] as String? : null,
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
    // Handle backend response format: {items, total, page, size, pages}
    // Convert from 1-based (backend) to 0-based (mobile) page
    final int backendPage = json['page'] as int? ?? 1;
    final int backendPages = json['pages'] as int? ?? 1;
    
    return CatalogPage(
      items: (json['items'] as List? ?? const [])
          .map((e) => Product.fromJson(e as Map<String, dynamic>))
          .toList(),
      page: backendPage - 1,  // Convert 1-based to 0-based
      totalPages: backendPages,
      total: json['total'] as int? ?? 0,
    );
  }
}