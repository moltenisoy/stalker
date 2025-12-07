# Refactorización de Configuración y Modo Ahorro

## Resumen de Cambios

Esta refactorización mejora significativamente el sistema de configuración y el modo de ahorro de rendimiento (Performance Mode) de la aplicación Stalker.

## Cambios en `core/config.py`

### Nuevas Características

1. **Validación Robusta de Datos**
   - Validación de tipos de datos para todos los campos de configuración
   - Valores por defecto robustos en caso de datos inválidos
   - Manejo de errores con backup automático de archivos corruptos

2. **Nuevos Métodos**
   - `set_hotkey(hotkey: str)`: Configura la tecla de acceso rápido global con validación
   - `get_ui(key: Optional[str])`: Obtiene valores de configuración de UI de forma segura
   - Funciones de validación privadas para UI, hotkey y módulos

3. **Mejoras en Manejo de Errores**
   - Backup automático de archivos de configuración corruptos (`.json.backup`)
   - Mensajes de error informativos
   - Valores por defecto seguros en caso de fallo

### Validaciones Implementadas

#### Configuración de UI
- **font_family**: Debe ser string
- **font_size**: Entero entre 8 y 24
- **theme**: Solo "dark" o "light"
- **opacity_active/inactive**: Float entre 0.0 y 1.0
- **accent**: Color hexadecimal válido (#RRGGBB o #RGB)
- **effects**: Boolean

#### Hotkey
- Debe ser string con formato "modifier+key"

## Cambios en `core/engine.py`

### Sincronización de Modo Ahorro

**Al activar Modo Ahorro:**
- Pausa el indexador de archivos
- Desactiva el asistente de IA
- Los efectos visuales se reducen automáticamente

**Al desactivar Modo Ahorro:**
- Reanuda el indexador de archivos
- Re-activa el asistente de IA si el módulo está habilitado
- Los efectos visuales se restauran

## Cambios en `ui/launcher.py`

### Aplicación Dinámica de Tema

La ventana ahora aplica automáticamente la configuración de tema:
1. Colores: Tema oscuro/claro desde config
2. Fuente: Familia y tamaño configurables
3. Opacidad: Valores activo/inactivo desde config
4. Efectos Visuales: Border radius se reduce en modo ahorro

## Cambios en `core/app.py`

### Integración de Configuración

1. Hotkey Global se lee desde config
2. Tema se aplica desde config al iniciar
3. Color de acento se usa el valor configurado

## Tests Implementados

Todos los tests están en `tests/` y validan:
- Valores por defecto
- Toggle de modo ahorro
- Validación de configuraciones
- Manejo de errores
- Persistencia de configuración

## Uso

```python
# Cambiar tema
config = ConfigManager()
config.set_ui(theme="light", accent="#ff0000")

# Configurar hotkey
config.set_hotkey("alt+space")

# Activar modo ahorro
config.toggle_performance_mode(True)
```

## Beneficios

1. Mayor robustez con manejo de errores
2. Más opciones de personalización
3. Modo ahorro funcional
4. Código testeado y mantenible
