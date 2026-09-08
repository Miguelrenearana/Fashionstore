import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';
import { Button } from '../ui/Button';
import { ShoppingBag, User, LogOut, Menu, X, Search } from 'lucide-react';
import { useState } from 'react';

export default function Header() {
  const location = useLocation();
  const { user, logout, isAuthenticated } = useAuth();
  const { itemCount } = useCart();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  const navLinks = [
    { path: '/', label: 'Inicio' },
    { path: '/productos', label: 'Productos' },
    { path: '/productos?category=mujer', label: 'Mujer' },
    { path: '/productos?category=hombre', label: 'Hombre' },
    { path: '/productos?category=ninos', label: 'Niños' },
    { path: '/productos?sale=true', label: 'Ofertas' },
  ];

  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="container-main">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link to="/" className="text-2xl font-bold text-primary-600" aria-label="FashionStore Home">
              FashionStore
            </Link>

            <nav className="hidden md:flex items-center gap-6" aria-label="Navegación principal">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`text-sm font-medium transition-colors duration-200 ${
                    location.pathname === link.path || location.pathname.startsWith(link.path + '?')
                      ? 'text-primary-600'
                      : 'text-gray-600 hover:text-primary-600'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSearchOpen(!isSearchOpen)}
              className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
              aria-label="Buscar productos"
              aria-expanded={isSearchOpen}
            >
              <Search className="w-5 h-5" />
              <span className="text-sm">Buscar...</span>
            </button>

            {isAuthenticated ? (
              <div className="relative">
                <Link
                  to="/carrito"
                  className="relative p-2 text-gray-600 hover:text-primary-600 transition-colors"
                  aria-label={`Carrito de compras, ${itemCount} artículos`}
                >
                  <ShoppingBag className="w-6 h-6" />
                  {itemCount > 0 && (
                    <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary-600 text-xs font-bold text-white">
                      {itemCount > 99 ? '99+' : itemCount}
                    </span>
                  )}
                </Link>
              </div>
            ) : null}

            <div className="hidden md:flex items-center gap-3">
              {isAuthenticated ? (
                <>
                  <Link to="/perfil" className="text-sm font-medium text-gray-600 hover:text-primary-600 transition-colors">
                    <User className="w-5 h-5 inline-block mr-1" />
                    Mi cuenta
                  </Link>
                  <Button variant="ghost" size="sm" onClick={logout}>
                    <LogOut className="w-4 h-4 mr-1" />
                    Salir
                  </Button>
                </>
              ) : (
                <>
                  <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-primary-600 transition-colors">
                    Iniciar sesión
                  </Link>
                  <Link to="/registro">
                    <Button size="sm">Registrarse</Button>
                  </Link>
                </>
              )}
            </div>

            <button
              className="md:hidden p-2 text-gray-600 hover:text-gray-900"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              aria-label={isMenuOpen ? 'Cerrar menú' : 'Abrir menú'}
              aria-expanded={isMenuOpen}
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {isSearchOpen && (
          <div className="sm:hidden py-4 border-t border-gray-100">
            <form className="flex gap-2" role="search">
              <input
                type="search"
                placeholder="Buscar productos..."
                className="flex-1 px-4 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500"
                aria-label="Buscar productos"
              />
              <Button type="submit" size="sm">Buscar</Button>
            </form>
          </div>
        )}

        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-100">
            <nav className="flex flex-col gap-2" aria-label="Menú móvil">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    location.pathname === link.path || location.pathname.startsWith(link.path + '?')
                      ? 'bg-primary-50 text-primary-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-primary-600'
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  {link.label}
                </Link>
              ))}
              <div className="pt-4 border-t border-gray-100 flex flex-col gap-2">
                {isAuthenticated ? (
                  <>
                    <Link
                      to="/perfil"
                      className="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-primary-600"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Mi cuenta
                    </Link>
                    <Button variant="ghost" className="w-full justify-start" onClick={() => { logout(); setIsMenuOpen(false); }}>
                      <LogOut className="w-4 h-4 mr-2" />
                      Cerrar sesión
                    </Button>
                  </>
                ) : (
                  <>
                    <Link
                      to="/login"
                      className="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-primary-600"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Iniciar sesión
                    </Link>
                    <Link to="/registro" onClick={() => setIsMenuOpen(false)}>
                      <Button className="w-full justify-start">Registrarse</Button>
                    </Link>
                  </>
                )}
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}