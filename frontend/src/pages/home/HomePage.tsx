import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { ShoppingBag, Sparkles, Truck, RotateCcw, Shield } from 'lucide-react';
import ProductCard from '../../components/product/ProductCard';

const heroSlides = [
  {
    title: 'Nueva Colección Primavera-Verano',
    subtitle: 'Descubre las últimas tendencias en moda',
    cta: 'Comprar ahora',
    href: '/productos?category=nuevo',
    background: 'bg-gradient-to-r from-pink-100 to-rose-100',
  },
  {
    title: 'Moda Sostenible',
    subtitle: 'Ropa ecológica con estilo',
    cta: 'Ver colección',
    href: '/productos?category=sostenible',
    background: 'bg-gradient-to-r from-green-100 to-emerald-100',
  },
  {
    title: 'Rebajas hasta 50%',
    subtitle: 'Tus favoritos a precios increíbles',
    cta: 'Ver ofertas',
    href: '/productos?sale=true',
    background: 'bg-gradient-to-r from-yellow-100 to-orange-100',
  },
];

const categories = [
  { name: 'Mujer', slug: 'mujer', image: 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400', itemCount: '240+' },
  { name: 'Hombre', slug: 'hombre', image: 'https://images.unsplash.com/photo-1456081473473-6e2b24a5c45e?w=400', itemCount: '180+' },
  { name: 'Niños', slug: 'ninos', image: 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400', itemCount: '120+' },
  { name: 'Accesorios', slug: 'accesorios', image: 'https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?w=400', itemCount: '90+' },
];

const featuredProducts = [
  { id: 1, name: 'Vestido Floral Verano', price: 49.99, discountPrice: 39.99, image: 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400', isNew: true },
  { id: 2, name: 'Camiseta Básica Algodón', price: 19.99, image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400' },
  { id: 3, name: 'Jeans Slim Fit', price: 59.99, discountPrice: 44.99, image: 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400', isSale: true },
  { id: 4, name: 'Chaqueta Bomber', price: 79.99, image: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400' },
  { id: 5, name: 'Zapatillas Running', price: 89.99, discountPrice: 69.99, image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400', isSale: true },
  { id: 6, name: 'Bolso Tote Cuero', price: 129.99, image: 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400' },
  { id: 7, name: 'Gafas de Sol Aviador', price: 34.99, image: 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400' },
  { id: 8, name: 'Reloj Minimalista', price: 149.99, discountPrice: 119.99, image: 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400', isSale: true },
];

const benefits = [
  { icon: Truck, title: 'Envío Gratis', desc: 'En pedidos +50€' },
  { icon: RotateCcw, title: 'Devoluciones 30 días', desc: 'Sin complicaciones' },
  { icon: Shield, title: 'Pago Seguro', desc: '100% protegido' },
  { icon: Sparkles, title: 'Novedades Semanales', desc: 'Siempre a la moda' },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Carousel */}
      <section className="relative h-[600px] md:h-[700px] overflow-hidden">
        <div className="absolute inset-0">
          {heroSlides.map((slide, index) => (
            <div
              key={index}
              className={`absolute inset-0 ${slide.background} flex items-center`}
            >
              <div className="container-main">
                <div className="max-w-2xl animate-fade-in-up">
                  <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-4 tracking-tight">
                    {slide.title}
                  </h1>
                  <p className="text-lg md:text-xl text-gray-600 mb-8">
                    {slide.subtitle}
                  </p>
                  <Link to={slide.href}>
                    <Button size="lg" className="w-auto">
                      {slide.cta}
                      <ShoppingBag className="w-5 h-5 ml-2" />
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Categories */}
      <section className="section bg-white">
        <div className="container-main">
          <div className="text-center mb-12">
            <h2 className="heading-2 mb-4">Compra por Categoría</h2>
            <p className="text-body max-w-2xl mx-auto">Encuentra tu estilo en nuestras colecciones</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {categories.map((category) => (
              <Link
                key={category.slug}
                to={`/productos?category=${category.slug}`}
                className="group relative aspect-[4/5] rounded-2xl overflow-hidden bg-gray-100"
              >
                <img
                  src={category.image}
                  alt={category.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent flex flex-col items-center justify-end p-6">
                  <h3 className="text-2xl font-bold text-white mb-1">{category.name}</h3>
                  <p className="text-white/80 text-sm">{category.itemCount} productos</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="section bg-gray-50">
        <div className="container-main">
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between mb-10">
            <div>
              <h2 className="heading-2 mb-2">Productos Destacados</h2>
              <p className="text-body">Nuestra selección de lo mejor de la semana</p>
            </div>
            <Link to="/productos" className="mt-4 sm:mt-0 text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1">
              Ver todos
              <ShoppingBag className="w-4 h-4" />
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="section bg-white">
        <div className="container-main">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {benefits.map((benefit) => (
              <div key={benefit.title} className="text-center p-6">
                <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-primary-100 flex items-center justify-center text-primary-600">
                  <benefit.icon className="w-8 h-8" aria-hidden="true" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{benefit.title}</h3>
                <p className="text-gray-600 text-sm">{benefit.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <section className="section bg-primary-600">
        <div className="container-main text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Suscríbete a nuestra Newsletter
          </h2>
          <p className="text-primary-100 mb-8 max-w-2xl mx-auto">
            Recibe un 10% de descuento en tu primera compra y sé el primero en enterarte de novedades y ofertas exclusivas.
          </p>
          <form className="max-w-md mx-auto flex flex-col sm:flex-row gap-3" action="#">
            <input
              type="email"
              placeholder="Tu email"
              className="flex-1 px-5 py-3 rounded-lg bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-300"
              required
              aria-label="Email para suscripción"
            />
            <Button type="submit" className="bg-white text-primary-600 hover:bg-gray-100 whitespace-nowrap">
              Suscribirme
            </Button>
          </form>
          <p className="text-primary-200 text-sm mt-4">
            Al suscribirte aceptas nuestra <a href="#" className="underline hover:text-white">Política de Privacidad</a>.
          </p>
        </div>
      </section>
    </div>
  );
}