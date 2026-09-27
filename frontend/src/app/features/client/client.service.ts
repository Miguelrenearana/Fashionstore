import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@core/environments/environment';

export interface Branch {
  id: number;
  name: string;
  city_id?: number;
  address?: string;
  phone?: string;
  is_active?: boolean;
}

export interface Category {
  id: number;
  name: string;
}

export interface CatalogItem {
  id: number;
  name: string;
  description?: string;
  price: number;
  base_price?: number;
  min_price?: number;
  discount_percentage?: number;
  sku?: string;
  images: string[];
  category_id?: number;
  category_name?: string;
  brand?: string;
  is_featured?: boolean;
  is_best_seller?: boolean;
  variants?: ProductVariant[];
}

export interface ProductVariant {
  id: number;
  size?: string;
  size_name?: string;
  color?: string;
  color_name?: string;
  stock: number;
  price?: number;
  base_price?: number;
  sku?: string;
  in_stock?: boolean;
}

export interface CatalogResponse {
  items: CatalogItem[];
  total: number;
  page: number;
  pages: number;
  size: number;
}

export interface CartItem {
  variant_id: number;
  product_id: number;
  name: string;
  price: number;
  quantity: number;
  size?: string;
  color?: string;
  image_url?: string;
  subtotal?: number;
}

export interface NotificationItem {
  id: number;
  type: string;
  title: string;
  body: string;
  is_read: boolean;
  read?: boolean;
  created_at: string;
}

export interface HistoryEntry {
  id: number;
  created_at: string;
  total: number;
  status: string;
  type: 'sale' | 'reservation';
  items_count?: number;
  payment_method?: string;
  items?: HistoryItem[];
  reservation_code?: string;
  branch_name?: string;
}

export interface HistoryItem {
  product_name: string;
  quantity: number;
  price: number;
  size?: string;
  color?: string;
  image_url?: string;
}

@Injectable({ providedIn: 'root' })
export class ClientService {
  constructor(private http: HttpClient) {}

  // CU-12/13 - Catálogo y búsqueda
  getCatalog(params: {
    page?: number;
    size?: number;
    search?: string;
    category_id?: number;
    branch_id?: number;
    sizes?: string;
    colors?: string;
    in_stock?: boolean;
    sort_by?: string;
  } = {}): Observable<CatalogResponse> {
    let p = new HttpParams();
    p = p.set('page', String(params.page ?? 1));
    p = p.set('size', String(params.size ?? 12));
    if (params.search) p = p.set('search', params.search);
    if (params.category_id) p = p.set('category_id', String(params.category_id));
    if (params.branch_id) p = p.set('branch_id', String(params.branch_id));
    if (params.sizes) p = p.set('sizes', params.sizes);
    if (params.colors) p = p.set('colors', params.colors);
    if (params.in_stock !== undefined) p = p.set('in_stock', String(params.in_stock));
    if (params.sort_by) p = p.set('sort_by', params.sort_by);
    return this.http.get<CatalogResponse>(`${environment.apiUrl}/catalog`, { params: p });
  }

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${environment.apiUrl}/catalog/categories`);
  }

  getProduct(id: number): Observable<any> {
    return this.http.get(`${environment.apiUrl}/catalog/${id}`);
  }

  // CU-14 - Disponibilidad por sucursal
  getBranches(): Observable<Branch[]> {
    return this.http.get<Branch[]>(`${environment.apiUrl}/locations/branches`);
  }

  getBranchAvailability(productId: number, branchId: number): Observable<any> {
    return this.http.get(`${environment.apiUrl}/catalog/${productId}`, {
      params: new HttpParams().set('branch_id', String(branchId)),
    });
  }

  // CU-20 - Carrito
  getCart(): Observable<{ items: CartItem[]; subtotal?: number; discount?: number; total?: number }> {
    return this.http.get<{ items: CartItem[] }>(`${environment.apiUrl}/cart`);
  }

  addCartItem(variantId: number, quantity: number): Observable<any> {
    return this.http.post(`${environment.apiUrl}/cart/items`, { variant_id: variantId, quantity });
  }

  updateCartItem(variantId: number, quantity: number): Observable<any> {
    return this.http.patch(`${environment.apiUrl}/cart/items/${variantId}`, { quantity });
  }

  removeCartItem(variantId: number): Observable<any> {
    return this.http.delete(`${environment.apiUrl}/cart/items/${variantId}`);
  }

  clearCart(): Observable<any> {
    return this.http.delete(`${environment.apiUrl}/cart`);
  }

  applyCoupon(code: string): Observable<{ discount: number }> {
    return this.http.post<{ discount: number }>(`${environment.apiUrl}/cart/coupon`, { code });
  }

  // CU-21/25 - Compra y pago
  checkout(shipping_address: any, payment_method: string): Observable<any> {
    return this.http.post(`${environment.apiUrl}/cart/purchase`, {
      shipping_address,
      payment_method,
    });
  }

  // CU-15/16 - Reservas
  getMyReservations(): Observable<any[]> {
    return this.http.get<any[]>(`${environment.apiUrl}/reservations/me`);
  }

  getReservation(id: number): Observable<any> {
    return this.http.get(`${environment.apiUrl}/reservations/${id}`);
  }

  createReservation(items: { variant_id: number; quantity: number }[], branchId?: number): Observable<any> {
    return this.http.post(`${environment.apiUrl}/reservations`, {
      items,
      branch_id: branchId,
    });
  }

  cancelReservation(id: number): Observable<any> {
    return this.http.patch(`${environment.apiUrl}/reservations/${id}/status`, { status: 'cancelled' });
  }

  // CU-22/26 - Historial y comprobantes
  getHistory(page = 1, size = 20): Observable<any> {
    const params = new HttpParams().set('page', String(page)).set('size', String(size));
    return this.http.get(`${environment.apiUrl}/history`, { params });
  }

  getReceipts(page = 1, size = 20): Observable<any> {
    const params = new HttpParams().set('page', String(page)).set('size', String(size));
    return this.http.get(`${environment.apiUrl}/receipts`, { params });
  }

  getReceipt(id: number): Observable<any> {
    return this.http.get(`${environment.apiUrl}/receipts/${id}`);
  }

  getSale(id: number): Observable<any> {
    return this.http.get(`${environment.apiUrl}/sales/${id}`);
  }

  // CU-05 - Perfil
  getMe(): Observable<any> {
    return this.http.get(`${environment.apiUrl}/users/me`);
  }

  getClientProfile(): Observable<any> {
    return this.http.get(`${environment.apiUrl}/clients/me`);
  }

  updateClientProfile(payload: any): Observable<any> {
    return this.http.patch(`${environment.apiUrl}/clients/me`, payload);
  }

  // Notificaciones
  getNotifications(limit = 200): Observable<NotificationItem[]> {
    const params = new HttpParams().set('limit', String(limit));
    return this.http.get<NotificationItem[]>(`${environment.apiUrl}/notifications`, { params });
  }

  markNotificationRead(id: number): Observable<any> {
    return this.http.patch(`${environment.apiUrl}/notifications/${id}/read`, {});
  }

  // CU-30 - Recomendaciones IA
  getRecommendations(source = 'trending', limit = 10, variantId?: number): Observable<any[]> {
    let params = new HttpParams().set('source', source).set('limit', String(limit));
    if (variantId) params = params.set('source_variant_id', String(variantId));
    return this.http.get<any[]>(`${environment.apiUrl}/ai/recommendations`, { params });
  }

  getTrending(limit = 10): Observable<any[]> {
    const params = new HttpParams().set('limit', String(limit));
    return this.http.get<any[]>(`${environment.apiUrl}/ai/recommendations/trending`, { params });
  }

  logProductView(variantId: number): Observable<any> {
    return this.http.post(`${environment.apiUrl}/ai/view/${variantId}`, {});
  }

  // CU-31 - Asistente IA
  aiChat(message: string, history: { role: 'user' | 'assistant'; content: string }[] = []): Observable<any> {
    return this.http.post(`${environment.apiUrl}/ai/chat`, { message, history });
  }
}