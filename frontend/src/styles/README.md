# Estilos de Minttu Dashboard

## Estructura de Carpetas

```
styles/
├── components/          # Estilos de componentes reutilizables
│   ├── sidebar.css     # Estilos del componente Sidebar
│   ├── topbar.css     # Estilos del componente TopBar
│   ├── buttons.css     # Estilos de botones reutilizables
│   └── index.css      # Índice de todos los componentes
├── utilities/          # Utilidades y helpers
│   ├── transitions.css # Animaciones y transiciones reutilizables
│   ├── typography.css  # Utilidades de tipografía
│   └── index.css      # Índice de todas las utilidades
├── login.css          # Estilos específicos de la página de login
└── minttu.css         # Variables CSS y estilos base del tema
```

## Uso

### Importar estilos de componentes
```typescript
import "@/styles/components/sidebar.css";
import "@/styles/components/topbar.css";
import "@/styles/components/buttons.css";
// O importar todos:
import "@/styles/components/index.css";
```

### Importar utilidades
```typescript
import "@/styles/utilities/transitions.css";
import "@/styles/utilities/typography.css";
// O importar todas:
import "@/styles/utilities/index.css";
```

## Componentes Disponibles

### Sidebar
- `.sidebar-container` - Contenedor principal
- `.sidebar-panel` - Panel interno
- `.nav-item` - Items de navegación
- `.user-avatar-container` - Contenedor del avatar de usuario

### TopBar
- `.topbar` - Barra superior
- `.page-title` - Título de la página actual

### Botones
- `.btn-primary` - Botón primario con tema Minttu
- `.submit-button` - Botón de envío de formularios

## Utilidades

### Transiciones
- `.slide-down-*` - Transición de deslizamiento hacia abajo
- `.slide-up-*` - Transición de deslizamiento hacia arriba

### Tipografía
- `.page-title-h1` - Título principal (H1)
- `.page-title-h2` - Título secundario (H2)
- `.page-title-h3` - Título terciario (H3)
- `.page-subtitle` - Subtítulo
- `.text-muted` - Texto en color gris
- `.text-primary` - Texto en color primario

