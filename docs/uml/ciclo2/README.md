# docs/uml/ciclo2/

Diagramas PlantUML (secuencia + comunicación) y tablas de caso de uso del **Ciclo 2**.

Numeración de casos de uso **oficial** del proyecto, agrupados por paquete:

```
ciclo2/
├─ autenticacion-usuarios/      (CU-03 recuperar contraseña, CU-05 registro y perfil de cliente)
├─ gestion-catalogo/            (CU-08 categorías/tallas/colores, CU-09 temporadas/colecciones,
│                                CU-10 proveedores)
├─ reservas/                    (CU-16 consulta/cancelación de reservas, CU-18 preparación de prendas,
│                                CU-19 probador AR móvil, CU-20 carrito de compras)
└─ ventas-pagos-inventario/     (CU-21 compra en línea, CU-23 venta presencial, CU-24 pago en caja
                                 y comprobante)
```

Estructura por caso de uso (plantilla 4 columnas:
`Actor → «UI» → «Controller» → «Model»`, en colaboración: Actor — Boundary — Controller — Entity):

```
ciclo2/ventas-pagos-inventario/CU-24/sequence.puml
ciclo2/ventas-pagos-inventario/CU-24/communication.puml
ciclo2/ventas-pagos-inventario/CU-24/CU-24.md
...
```

Ver convenciones en RULES.md §6.