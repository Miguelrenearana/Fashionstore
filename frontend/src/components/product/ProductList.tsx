import { Link } from 'react-router-dom';
import ProductCard from './ProductCard';

interface Product {
  id: number;
  name: string;
  price: number;
  discountPrice?: number;
  image: string;
  isNew?: boolean;
  isSale?: boolean;
}

interface ProductListProps {
  products: Product[];
  title?: string;
  showViewAll?: boolean;
  viewAllHref?: string;
}

export default function ProductList({ products, title, showViewAll = false, viewAllHref }: ProductListProps) {
  if (products.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500 text-lg">No se encontraron productos</p>
      </div>
    );
  }

  return (
    <section className="section bg-gray-50" aria-labelledby={title ? 'products-heading' : undefined}>
      <div className="container-main">
        {(title || showViewAll) && (
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between mb-8">
            {title && (
              <h2 id="products-heading" className="heading-2 mb-4 sm:mb-0">
                {title}
              </h2>
            )}
            {showViewAll && viewAllHref && (
              <Link
                to={viewAllHref}
                className="mt-4 sm:mt-0 text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
              >
                Ver todos
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            )}
          </div>
        )}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </div>
    </section>
  );
}

export default ProductList;