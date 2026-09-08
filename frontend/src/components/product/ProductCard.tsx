import { Link } from 'react-router-dom';
import { Heart, ShoppingBag, Tag } from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { useState } from 'react';

interface Product {
  id: number;
  name: string;
  price: number;
  discountPrice?: number;
  image: string;
  isNew?: boolean;
  isSale?: boolean;
}

interface ProductCardProps {
  product: Product;
  compact?: boolean;
}

export default function ProductCard({ product, compact = false }: ProductCardProps) {
  const { addItem } = useCart();
  const [isWishlisted, setIsWishlisted] = useState(false);

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    addItem({
      id: product.id,
      name: product.name,
      price: product.discountPrice || product.price,
      image: product.image,
      quantity: 1,
    });
  };

  const handleToggleWishlist = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsWishlisted(!isWishlisted);
  };

  const displayPrice = product.discountPrice || product.price;
  const hasDiscount = product.discountPrice && product.discountPrice < product.price;
  const discountPercent = hasDiscount 
    ? Math.round(((product.price - product.discountPrice!) / product.price) * 100)
    : 0;

  return (
    <article className="card group relative">
      <Link
        to={`/productos/${product.name.toLowerCase().replace(/\s+/g, '-')}-${product.id}`}
        className="block"
        aria-label={`Ver detalles de ${product.name}`}
      >
        <div className="relative aspect-[3/4] overflow-hidden bg-gray-100">
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
          />
          
          {/* Badges */}
          <div className="absolute top-3 left-3 flex flex-col gap-1.5">
            {product.isNew && (
              <span className="px-2 py-0.5 text-xs font-medium bg-primary-600 text-white rounded">
                Nuevo
              </span>
            )}
            {hasDiscount && (
              <span className="px-2 py-0.5 text-xs font-medium bg-red-600 text-white rounded">
                -{discountPercent}%
              </span>
            )}
          </div>

          {/* Wishlist */}
          <button
            onClick={handleToggleWishlist}
            className="absolute top-3 right-3 w-9 h-9 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center text-gray-600 hover:text-red-500 hover:bg-white transition-colors opacity-0 group-hover:opacity-100 translate-y-2 group-hover:translate-y-0 transition-all duration-200"
            aria-label={isWishlisted ? 'Quitar de favoritos' : 'Añadir a favoritos'}
          >
            <Heart 
              className={`w-5 h-5 ${isWishlisted ? 'fill-current' : ''}`} 
              strokeWidth={isWishlisted ? 0 : 2} 
            />
          </button>

          {/* Quick Add to Cart */}
          <button
            onClick={handleAddToCart}
            className="absolute bottom-3 left-1/2 -translate-x-1/2 w-full max-w-[200px] px-4 py-2 bg-primary-600 text-white rounded-lg font-medium text-sm opacity-0 group-hover:opacity-100 translate-y-4 group-hover:translate-y-0 transition-all duration-200 flex items-center justify-center gap-2"
            aria-label={`Añadir ${product.name} al carrito`}
          >
            <ShoppingBag className="w-4 h-4" />
            Añadir al carrito
          </button>
        </div>

        <div className="p-4">
          <h3 className="font-medium text-gray-900 mb-1 line-clamp-1 group-hover:text-primary-600 transition-colors">
            {product.name}
          </h3>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-gray-900">
              {displayPrice.toFixed(2)}€
            </span>
            {hasDiscount && (
              <span className="text-sm text-gray-400 line-through">
                {product.price.toFixed(2)}€
              </span>
            )}
          </div>
        </div>
      </Link>
    </article>
  );
}

export default ProductCard;