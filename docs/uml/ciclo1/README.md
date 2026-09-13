# docs/uml/ciclo1/

Diagramas PlantUML (secuencia + comunicación) y tablas de caso de uso del **Ciclo 1**.

Numeración de casos de uso **oficial** del proyecto, agrupados por paquete:

```
ciclo1/
├─ autenticacion-usuarios/      (CU-01 sesión, CU-02 cierre, CU-04 usuarios y roles)
├─ gestion-catalogo/            (CU-06 ciudades/sucursales, CU-07 productos, CU-12 catálogo,
│                                CU-13 búsqueda/filtros, CU-14 disponibilidad por sucursal)
└─ reservas/                    (CU-15 reservas múltiples prendas, CU-17 recepción y atención)
```

Estructura por caso de uso (plantilla 4 columnas:
`Actor → «UI» → «Controller» → «Model»`, en colaboración: Actor — Boundary — Controller — Entity):

```
ciclo1/gestion-catalogo/CU-12/sequence.puml
ciclo1/gestion-catalogo/CU-12/communication.puml
ciclo1/gestion-catalogo/CU-12/CU-12.md
...
```

Ver convenciones en RULES.md §6.