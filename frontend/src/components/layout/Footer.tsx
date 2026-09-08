import { Link } from 'react-router-dom';
import { Facebook, Instagram, Twitter, Youtube, Mail, Truck, Shield, RotateCcw, Headphones } from 'lucide-react';

const footerLinks = {
  empresa: [
    { label: 'Nosotros', href: '#' },
    { label: 'Tiendas físicas', href: '#' },
    { label: 'Trabaja con nosotros', href: '#' },
    { label: 'Sostenibilidad', href: '#' },
    { label: 'Blog', href: '#' },
  ],
  ayuda: [
    { label: 'Preguntas frecuentes', href: '#' },
    { label: 'Envíos y devoluciones', href: '#' },
    { label: 'Guía de tallas', href: '#' },
    { label: 'Métodos de pago', href: '#' },
    { label: 'Contacto', href: '#' },
  ],
  legal: [
    { label: 'Términos y condiciones', href: '#' },
    { label: 'Política de privacidad', href: '#' },
    { label: 'Política de cookies', href: '#' },
    { label: 'Aviso legal', href: '#' },
  ],
  contacto: {
    email: 'hola@fashionstore.com',
    phone: '+34 900 123 456',
    address: 'Calle Moda 123, 28001 Madrid, España',
  },
};

const socialLinks = [
  { icon: Facebook, href: '#', label: 'Facebook' },
  { icon: Instagram, href: '#', label: 'Instagram' },
  { icon: Twitter, href: '#', label: 'Twitter' },
  { icon: Youtube, href: '#', label: 'YouTube' },
];

const benefits = [
  { icon: Truck, title: 'Envío gratis', description: 'En pedidos superiores a 50€' },
  { icon: Shield, title: 'Pago seguro', description: '100% protegido' },
  { icon: RotateCcw, title: 'Devoluciones fáciles', description: '30 días para cambiar de opinión' },
  { icon: Headphones, title: 'Atención al cliente', description: 'Lun-Vie 9:00-18:00' },
];

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300" role="contentinfo">
      <div className="container-main py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12">
          <div className="lg:col-span-2">
            <Link to="/" className="text-2xl font-bold text-white mb-4 block">
              FashionStore
            </Link>
            <p className="text-gray-400 max-w-sm mb-6">
              Tu tienda de moda online con las últimas tendencias para mujer, hombre y niños. 
              Calidad, estilo y los mejores precios.
            </p>
            <div className="flex gap-4">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 hover:bg-gray-700 hover:text-white transition-colors"
                  aria-label={social.label}
                >
                  <social.icon className="w-5 h-5" aria-hidden="true" />
                </a>
              ))}
            </div>
          </div>

          <nav aria-label="Enlaces de empresa">
            <h3 className="text-white font-semibold mb-4">Empresa</h3>
            <ul className="space-y-3">
              {footerLinks.empresa.map((link) => (
                <li key={link.label}>
                  <Link to={link.href} className="hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <nav aria-label="Enlaces de ayuda">
            <h3 className="text-white font-semibold mb-4">Ayuda</h3>
            <ul className="space-y-3">
              {footerLinks.ayuda.map((link) => (
                <li key={link.label}>
                  <Link to={link.href} className="hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <nav aria-label="Enlaces legales">
            <h3 className="text-white font-semibold mb-4">Legal</h3>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.label}>
                  <Link to={link.href} className="hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-800">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            {benefits.map((benefit) => (
              <div key={benefit.title} className="flex items-start gap-3">
                <div className="w-12 h-12 rounded-lg bg-gray-800 flex items-center justify-center text-primary-500 flex-shrink-0">
                  <benefit.icon className="w-6 h-6" aria-hidden="true" />
                </div>
                <div>
                  <h4 className="font-medium text-white">{benefit.title}</h4>
                  <p className="text-sm text-gray-400">{benefit.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="flex flex-col md:flex-row items-center justify-between gap-4 pt-8 border-t border-gray-800">
            <p className="text-sm text-gray-400">
              © {new Date().getFullYear()} FashionStore. Todos los derechos reservados.
            </p>
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400">
              <span>Contacto:</span>
              <a href={`mailto:${footerLinks.contacto.email}`} className="hover:text-white transition-colors">
                {footerLinks.contacto.email}
              </a>
              <span className="hidden sm:inline">·</span>
              <a href={`tel:${footerLinks.contacto.phone}`} className="hover:text-white transition-colors">
                {footerLinks.contacto.phone}
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}