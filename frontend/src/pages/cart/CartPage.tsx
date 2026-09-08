import { Link } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import { Button } from '../../components/ui/Button';
import { Trash2, Plus, Minus, ShoppingBag, ArrowLeft } from 'lucide-react';

export default function CartPage() {
  const { items, subtotal, updateQuantity, removeItem, clearCart, itemCount } = useCart();

  const shippingCost = subtotal >= 50 || subtotal === 0 ? 0 : 4.99;
  const tax = subtotal * 0.21;
  const total = subtotal + shippingCost + tax;

  if (items.length === 0) {
    return (
      <div className="section bg-gray-50">
        <div className="container-main text-center py-16">
          <ShoppingBag className="w-16 h-16 mx-auto text-gray-300 mb-6" />
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Tu carrito está vacío</h1>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            Parece que aún no has añadido ningún producto. ¡Explora nuestra tienda y encuentra tus favoritos!
          </p>
          <Link to="/productos">
            <Button size="lg">
              <ArrowLeft className="w-5 h-5 mr-2" />
              Seguir comprando
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="section bg-gray-50">
      <div className="container-main">
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Carrito de compras ({itemCount})</h1>
            
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full" role="table">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-100">
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Producto</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Precio</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Cantidad</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Subtotal</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {items.map((item) => (
                      <tr key={`${item.id}-${item.size || ''}-${item.color || ''}`} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-4">
                            <img
                              src={item.image}
                              alt={item.name}
                              className="w-20 h-20 object-cover rounded-lg"
                            />
                            <div>
                              <h3 className="font-medium text-gray-900">{item.name}</h3>
                              {item.size && <p className="text-sm text-gray-500">Talla: {item.size}</p>}
                              {item.color && <p className="text-sm text-gray-500">Color: {item.color}</p>}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-gray-900 font-medium">
                          {item.price.toFixed(2)}€
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => updateQuantity(item.id, item.quantity - 1, item.size, item.color)}
                              disabled={item.quantity <= 1}
                              className="w-8 h-8 rounded-lg border border-gray-300 flex items-center justify-center text-gray-600 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                              aria-label="Disminuir cantidad"
                            >
                              <Minus className="w-4 h-4" />
                            </button>
                            <span className="w-10 text-center font-medium">{item.quantity}</span>
                            <button
                              onClick={() => updateQuantity(item.id, item.quantity + 1, item.size, item.color)}
                              className="w-8 h-8 rounded-lg border border-gray-300 flex items-center justify-center text-gray-600 hover:bg-gray-100"
                              aria-label="Aumentar cantidad"
                            >
                              <Plus className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-gray-900 font-medium">
                          {(item.price * item.quantity).toFixed(2)}€
                        </td>
                        <td className="px-6 py-4">
                          <button
                            onClick={() => removeItem(item.id, item.size, item.color)}
                            className="text-gray-400 hover:text-red-600 transition-colors p-2"
                            aria-label={`Eliminar ${item.name} del carrito`}
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="px-6 py-4 border-t border-gray-100 flex justify-between items-center">
                <Button variant="ghost" onClick={clearCart} disabled={items.length === 0}>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Vaciar carrito
                </Button>
                <Link to="/productos">
                  <Button variant="outline">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Seguir comprando
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 sticky top-24">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Resumen del pedido</h2>
              
              <dl className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-600">Subtotal</dt>
                  <dd className="font-medium text-gray-900">{subtotal.toFixed(2)}€</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">Envío</dt>
                  <dd className="font-medium text-gray-900">
                    {shippingCost === 0 ? (
                      <span className="text-green-600">Gratis</span>
                    ) : (
                      `${shippingCost.toFixed(2)}€`
                    )}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">IVA (21%)</dt>
                  <dd className="font-medium text-gray-900">{tax.toFixed(2)}€</dd>
                </div>
              </dl>

              {subtotal > 0 && subtotal < 50 && (
                <p className="mt-4 text-sm text-gray-500">
                  Añade <span className="font-medium text-primary-600">{(50 - subtotal).toFixed(2)}€</span> más para envío gratis
                </p>
              )}

              <div className="border-t border-gray-100 pt-4 mt-4">
                <div className="flex justify-between text-lg font-bold">
                  <span>Total</span>
                  <span>{total.toFixed(2)}€</span>
                </div>
              </div>

              <Link to="/checkout" className="block mt-6">
                <Button className="w-full" size="lg">
                  Proceder al pago
                  <ShoppingBag className="w-5 h-5 ml-2" />
                </Button>
              </Link>

              <p className="mt-4 text-center text-xs text-gray-500">
                Pago seguro · Envío 24-48h · Devoluciones 30 días
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}