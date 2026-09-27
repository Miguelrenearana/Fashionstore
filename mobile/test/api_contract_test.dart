import 'package:flutter_test/flutter_test.dart';

import 'package:fashionstore_mobile/core/models/catalog.dart';
import 'package:fashionstore_mobile/core/models/models.dart';
import 'package:fashionstore_mobile/features/cart/checkout_screen.dart';
import 'package:fashionstore_mobile/features/profile/purchase_history_screen.dart';

/// Pruebas de contrato contra la API real.
///
/// Los fixtures son respuestas literales de `GET /sales?mine=true`,
/// `GET /cart`, `GET /ai/recommendations` y `POST /cart/purchase`. Existen
/// porque el parsing de esas pantallas estaba desacoplado del backend y por eso
/// se rompia en silencio: la appia mostrar compras y pagos inventados, y las
/// recomendaciones fallaban al leer `product` anidado cuando la API devuelve
/// una lista plana.
void main() {
  group('Purchase.fromJson (CU-22, GET /sales?mine=true)', () {
    final payload = <String, dynamic>{
      'id': 11,
      'invoice_number': 'FAC-20260927062805913646',
      'branch_id': 1,
      'client_id': 2,
      'reservation_id': null,
      'total_amount': 540.0,
      'payment_method': 'static_qr',
      'status': 'PENDING',
      'paid_at': null,
      'created_at': '2026-09-27T06:28:08.264655Z',
      'items_count': 3,
      'details': [
        {
          'id': 1,
          'variant_id': 4,
          'quantity': 2,
          'unit_price': 180.0,
          'line_total': 360.0,
          'sku': 'CAMISA-S-NE-9D3A9B',
          'garment_id': 1,
          'garment_name': 'Camisa Oxford Basica',
          'image_url': 'https://cdn.fashionstore.dev/camisa-1.png',
          'size_name': 'S',
          'color_name': 'Negro',
        },
      ],
    };

    test('reads total_amount, not total', () {
      final purchase = Purchase.fromJson(payload);
      expect(purchase.total, 540.0);
    });

    test('reads invoice number and creation date', () {
      final purchase = Purchase.fromJson(payload);
      expect(purchase.invoiceNumber, 'FAC-20260927062805913646');
      expect(purchase.date.year, 2026);
      expect(purchase.date.month, 9);
      expect(purchase.date.day, 27);
    });

    test('reads items count, method and status', () {
      final purchase = Purchase.fromJson(payload);
      expect(purchase.itemsCount, 3);
      expect(purchase.paymentMethod, 'static_qr');
      expect(purchase.status, 'PENDING');
    });

    test('a pending sale has no receipt available', () {
      // El backend responde 404 "pay first" hasta que se paga la venta.
      expect(Purchase.fromJson(payload).hasReceipt, isFalse);
    });

    test('a completed sale exposes the receipt', () {
      final paid = {...payload, 'status': 'COMPLETED', 'paid_at': '2026-09-27T06:29:00Z'};
      final purchase = Purchase.fromJson(paid);
      expect(purchase.isCompleted, isTrue);
      expect(purchase.hasReceipt, isTrue);
    });

    test('parses enriched line items', () {
      final purchase = Purchase.fromJson(payload);
      expect(purchase.details, hasLength(1));
      final line = purchase.details.single;
      expect(line.quantity, 2);
      expect(line.garmentName, 'Camisa Oxford Basica');
      expect(line.sizeName, 'S');
      expect(line.colorName, 'Negro');
      expect(line.imageUrl, isNotEmpty);
      expect(line.unitPrice, 180.0);
    });

    test('tolerates a sale without details', () {
      final purchase = Purchase.fromJson({
        ...payload,
        'details': <dynamic>[],
        'items_count': 0,
      });
      expect(purchase.details, isEmpty);
      expect(purchase.total, 540.0);
    });
  });

  group('ProductRecommendation.fromJson (CU-30, /ai/recommendations)', () {
    test('parses the flat list item shape', () {
      final rec = ProductRecommendation.fromJson({
        'variant_id': 7,
        'variant_sku': 'HOODIE-M-AZ-11B2C3',
        'garment_name': 'Sudadera Hoodie',
        'garment_image_url': 'https://cdn.fashionstore.dev/hoodie-2.png',
        'size_name': 'M',
        'color_name': 'Azul',
        'price': 249.9,
        'score': 0.4691,
      });
      expect(rec.variantId, 7);
      expect(rec.variantSku, 'HOODIE-M-AZ-11B2C3');
      expect(rec.product.name, 'Sudadera Hoodie');
      expect(rec.product.price, 249.9);
      expect(rec.product.images.single,
          'https://cdn.fashionstore.dev/hoodie-2.png');
      expect(rec.sizeName, 'M');
      expect(rec.colorName, 'Azul');
      expect(rec.score, closeTo(0.4691, 0.0001));
    });

    test('still supports a nested product shape', () {
      final rec = ProductRecommendation.fromJson({
        'score': 0.8,
        'reason': 'Porque te gusta el denim',
        'product': {
          'id': 3,
          'name': 'Jeans Slim',
          'price': 320.0,
          'images': ['https://cdn.fashionstore.dev/jeans.png'],
        },
      });
      expect(rec.product.id, 3);
      expect(rec.product.name, 'Jeans Slim');
      expect(rec.reason, 'Porque te gusta el denim');
    });

    test('falls back gracefully on an empty item', () {
      final rec = ProductRecommendation.fromJson(<String, dynamic>{});
      expect(rec.product.name, 'Prenda');
      expect(rec.product.price, 0);
      expect(rec.variantId, isNull);
    });
  });

  group('OrderResult.fromJson (CU-21/CU-25, POST /cart/purchase)', () {
    test('parses the sale and payment envelope', () {
      final result = OrderResult.fromJson({
        'sale': {
          'id': 11,
          'invoice_number': 'FAC-20260927062805913646',
          'total_amount': 540.0,
          'status': 'PENDING',
          'items_count': 3,
        },
        'payment': {
          'id': 9,
          'amount': 540.0,
          'method': 'static_qr',
          'status': 'PENDING',
          'gateway_reference': 'QR-9C1A2B',
        },
      });
      expect(result.invoiceNumber, 'FAC-20260927062805913646');
      expect(result.total, 540.0);
      expect(result.saleStatus, 'PENDING');
      expect(result.paymentStatus, 'PENDING');
      expect(result.reference, 'QR-9C1A2B');
    });

    test('tolerates a payment without gateway reference', () {
      final result = OrderResult.fromJson({
        'sale': {'invoice_number': 'FAC-1', 'total_amount': 10.0},
        'payment': {'status': 'COMPLETED', 'method': 'card'},
      });
      expect(result.reference, isNull);
      expect(result.paymentStatus, 'COMPLETED');
      expect(result.invoiceNumber, 'FAC-1');
    });
  });

  group('CartItem.fromJson (CU-20, GET /cart)', () {
    test('reads the server total from details', () {
      final item = CartItem.fromJson({
        'variant_id': 4,
        'garment_id': 1,
        'garment_name': 'Camisa Oxford Basica',
        'quantity': 2,
        'unit_price': 180.0,
        'line_total': 360.0,
        'size_name': 'S',
        'color_name': 'Negro',
        'image_url': 'https://cdn.fashionstore.dev/camisa-1.png',
        'available': 5,
      });
      expect(item.quantity, 2);
      expect(item.name, 'Camisa Oxford Basica');
      expect(item.productId, 1);
      expect(item.size, 'S');
      expect(item.color, 'Negro');
      expect(item.variantLabel, 'S · Negro');
      expect(item.subtotal, 360.0);
      expect(item.available, 5);
    });
  });

  group('Product price handling', () {
    test('keeps the price coming from the API', () {
      final product = Product(
        id: 7,
        name: 'Sudadera Hoodie',
        price: 249.9,
        images: ['https://cdn.fashionstore.dev/hoodie.png'],
      );
      expect(product.finalPrice, 249.9);
      expect(product.hasDiscount, isFalse);
    });
  });
}
