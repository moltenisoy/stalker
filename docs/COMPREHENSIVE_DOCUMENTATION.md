# Stalker - Documentación Completa

## Índice

1. [Visión General](#visión-general)
2. [Características Principales](#características-principales)
3. [Funciones Detalladas](#funciones-detalladas)
4. [Nuevas Características](#nuevas-características)
5. [Uso y Comandos](#uso-y-comandos)
6. [Guía de Automatización](#guía-de-automatización)
7. [Configuración](#configuración)
8. [Solución de Problemas](#solución-de-problemas)

---

## Visión General

Stalker es un lanzador de aplicaciones inteligente y potente para Windows que combina búsqueda rápida, automatización contextual, y gestión de productividad. Con procesamiento local para privacidad y velocidad, Stalker ofrece:

- **Búsqueda instantánea** de aplicaciones, archivos, notas y más
- **Intent Router local** que detecta intenciones y propone acciones compuestas
- **Perfiles contextuales** que adaptan acciones según la aplicación activa
- **Automatización declarativa** mediante Flow Commands DSL
- **Acciones rápidas** sobre texto y archivos (limpiar formato, extraer enlaces, etc.)
- **IA opcional** con BYOK (Bring Your Own Key)
- **Monitor de sistema** con overlay persistente

---

## Características Principales

### 1. Búsqueda Universal

**Comandos disponibles:**

- **Buscar aplicaciones**: Escribe el nombre de cualquier app instalada
- **`/files [query]`**: Buscar en el índice de archivos
- **`/clipboard`**: Historial del portapapeles
- **`/snippets`**: Gestión de snippets de texto
- **`/links`**: Enlaces rápidos personalizados
- **`/macros`**: Macros grabadas
- **`/notes`**: Notas Markdown seguras
- **`/syshealth`**: Monitor de sistema y procesos
- **`/ai [prompt]`** o **`> [prompt]`**: Asistente de IA
- **`/context`**: Acciones contextuales para la app activa
- **`/actions`**: Acciones rápidas sobre el portapapeles
- **`>config`**: Panel de configuración

### 2. Calculadora Integrada

Realiza cálculos matemáticos directamente en el lanzador:
- Operaciones básicas: `2 + 2`, `10 * 5`
- Operaciones avanzadas: `sqrt(16)`, `sin(45)`, `log(10)`
- Constantes: `pi`, `e`

### 3. Gestión de Snippets

**Características:**
- Expansión de snippets con triggers (`@trigger` o `;trigger`)
- Asignación de hotkeys globales
- Almacenamiento encriptado
- Búsqueda rápida de snippets

**Uso:**
1. Crear snippet: `/snippets nuevo`
2. Definir trigger (ej: `@email`)
3. Escribir el contenido
4. Usar en cualquier lugar escribiendo `@email`

### 4. Índice de Archivos

**Características:**
- Indexación automática de drives locales
- Búsqueda instantánea por nombre
- Acciones: abrir, copiar ruta, abrir carpeta contenedora
- Modo de bajo consumo (pausa el indexador)

**Uso:**
- `/files documento.pdf` - Buscar archivos
- Click: Abrir archivo
- Ctrl+C: Copiar ruta
- Acciones adicionales en metadata

### 5. Historial de Portapapeles

**Características:**
- Monitoreo automático del portapapeles
- Almacena texto, imágenes, URLs y rutas de archivos
- Búsqueda en historial
- Restauración de elementos anteriores

**Uso:**
- `/clipboard` - Ver historial completo
- `/clipboard [query]` - Buscar en historial
- Click: Copiar al portapapeles
- Enter: Pegar en la app activa

### 6. Enlaces Rápidos (Quicklinks)

**Características:**
- URLs y comandos del sistema con alias
- Apertura rápida de sitios web
- Ejecución de comandos

**Uso:**
- Crear link: `/links agregar`
- Usar: escribir el alias directamente

### 7. Grabación de Macros

**Características:**
- Grabar secuencias de teclas
- Reproducir macros con hotkey o comando
- Útil para tareas repetitivas

**Uso:**
1. `/macros grabar` - Iniciar grabación
2. Realizar acciones
3. `/macros detener` - Finalizar
4. Asignar nombre y hotkey
5. Reproducir con hotkey o `/macros [nombre]`

### 8. Sistema de Notas

**Características:**
- Notas Markdown con encriptación
- Tags para organización
- Búsqueda full-text
- Editor integrado
- Inserción desde portapapeles

**Uso:**
- `/notes` - Ver todas las notas
- `/notes [query]` - Buscar notas
- Crear: `/notes nueva` o "Crear nota rápida"
- Insertar desde portapapeles: opción en resultados

### 9. Monitor de Sistema (SysHealth)

**Características:**
- Monitoreo en tiempo real: CPU, RAM, Disco, Red
- Lista de procesos con uso de recursos
- Acceso rápido a herramientas del sistema
- Overlay persistente opcional

**Información mostrada:**
- % CPU en uso
- RAM usado/total (GB)
- Velocidad lectura/escritura disco (MB/s)
- Velocidad subida/bajada red (MB/s)
- Top procesos por uso

**Herramientas del sistema:**
- Task Manager
- Aplicaciones de inicio
- Defragmentador de disco
- Monitor de recursos
- Liberador de espacio
- Información del sistema

**Uso:**
- `/syshealth` - Ver información del sistema
- `/overlay` - Toggle del overlay persistente
- Ctrl+W sobre proceso: Terminar proceso

### 10. Asistente de IA (Opcional)

**Características:**
- Integración con OpenAI/Azure/Gemini
- BYOK (Bring Your Own Key) para privacidad
- Respuestas en panel dedicado
- Guardar respuestas como notas

**Uso:**
- `/ai [pregunta]` o `> [pregunta]`
- Configurar API key en Settings > AI

---

## Nuevas Características

### 🎯 Intent Router (Detección de Intenciones)

El Intent Router analiza tus comandos localmente y detecta automáticamente qué quieres hacer, proponiendo acciones relevantes.

**Intenciones detectadas:**
- **Abrir aplicaciones**: "open chrome", "launch vscode"
- **Buscar archivos**: "find documento.pdf", "file: imagen.jpg"
- **Pegar snippets**: "@email", ";firma"
- **Acciones del sistema**: "lock", "shutdown", "volume up"
- **Transformar texto**: "uppercase", "clean format", "convert"
- **Traducir**: "translate hello", "traducir texto"
- **Calcular**: "2+2", "sqrt(16)"

**Ventajas:**
- ✅ 100% local (sin enviar datos a la nube)
- ✅ Privacidad total
- ✅ Respuesta instantánea
- ✅ Sugerencias inteligentes

### 🔗 Compound Actions (Acciones Compuestas)

Encadena múltiples acciones en un solo comando. Ideal para workflows complejos.

**Acciones compuestas predefinidas:**

1. **Zip y Compartir**
   - Comprimir archivo(s)
   - Copiar ruta del ZIP al portapapeles
   - Uso: Selecciona archivo, ejecuta acción

2. **Copiar Ruta y Abrir Carpeta**
   - Copiar ruta completa del archivo
   - Abrir la carpeta contenedora
   - Útil para compartir ubicaciones

3. **Convertir y Pegar**
   - Transformar texto (mayúsculas, minúsculas, etc.)
   - Pegar resultado automáticamente

4. **Traducir y Pegar**
   - Traducir texto del portapapeles
   - Pegar traducción

5. **Limpiar y Pegar**
   - Eliminar formato del texto
   - Eliminar espacios extra
   - Pegar como texto plano

**Uso:**
- Las acciones compuestas aparecen automáticamente según el contexto
- También disponibles en `/actions`

### 🎯 Context Profiles (Perfiles Contextuales)

Stalker detecta la aplicación activa y ofrece acciones específicas para esa app.

**Perfiles predefinidos:**

#### **Visual Studio Code**
- **Buscar símbolos** (Ctrl+T)
- **Buscar archivo** (Ctrl+P)
- **Toggle terminal** (Ctrl+`)
- Snippets específicos:
  - `@log` → `console.log('...', ...);`
  - `@func` → función JavaScript
  - `@class` → clase JavaScript

#### **Navegadores (Chrome/Firefox/Edge)**
- **Guardar sesión de pestañas**
- **Restaurar sesión**
- **Extraer enlaces** de la página

#### **Figma**
- **Exportar selección**

#### **Explorador de Archivos**
- **Copiar ruta completa** (Ctrl+Shift+C)
- **Abrir terminal aquí** (Ctrl+Shift+T)

**Crear perfiles personalizados:**
1. Usa `/context` para ver el contexto actual
2. Los perfiles se guardan en `~/.stalker/profiles/`
3. Edita JSON para personalizar acciones

**Formato del perfil:**
```json
{
  "app_name": "myapp",
  "display_name": "Mi Aplicación",
  "window_title_pattern": "My App",
  "actions": [
    {
      "name": "action_name",
      "description": "Descripción",
      "trigger": "ctrl+shift+a",
      "action_type": "command",
      "action_data": {"command": "..."}
    }
  ],
  "snippets": {
    "@trigger": "texto expandido"
  }
}
```

### ⚡ Flow Commands (Comandos de Flujo)

DSL declarativa para crear automatizaciones sin código nativo.

**Tipos de acciones disponibles:**
- `keystroke`: Enviar teclas
- `clipboard`: Leer/escribir portapapeles
- `command`: Ejecutar comando del sistema
- `wait`: Esperar N segundos
- `paste`: Pegar texto
- `copy`: Copiar al portapapeles
- `open`: Abrir archivo/carpeta
- `save`: Guardar (Ctrl+S)
- `transform`: Transformar texto

**Flows predefinidos:**

1. **copy_current_path** (Explorador de Archivos)
   - Focus barra de direcciones (Alt+D)
   - Copiar (Ctrl+C)
   - Cerrar barra (Escape)

2. **open_terminal_here** (Explorador de Archivos)
   - Obtener ruta actual
   - Abrir CMD en esa ubicación

3. **extract_links** (Navegador)
   - Leer portapapeles
   - Extraer URLs
   - Copiar lista de URLs

4. **clean_and_paste** (Universal)
   - Leer portapapeles
   - Limpiar formato
   - Pegar resultado

**Crear Flow personalizado:**

Crear archivo JSON en `~/.stalker/flows/`:

```json
{
  "name": "my_flow",
  "description": "Mi flujo personalizado",
  "app_context": "any",
  "steps": [
    {
      "action": "clipboard",
      "params": {"operation": "get"}
    },
    {
      "action": "transform",
      "params": {"type": "uppercase"}
    },
    {
      "action": "paste",
      "params": {"text": "${transformed_text}"}
    }
  ],
  "variables": {}
}
```

**Variables disponibles:**
- `${clipboard_content}` - Contenido del portapapeles
- `${transformed_text}` - Resultado de transformación
- Variables personalizadas definidas en el flow

### 🚀 Contextual Actions (Acciones Contextuales)

Acciones rápidas de un toque sobre texto y archivos.

**Acciones de pegado:**
- **Pegar Texto Plano**: Sin formato, IME-safe
- **Pegar y Navegar**: Para URLs (pega y presiona Enter)

**Transformaciones de texto:**
- **MAYÚSCULAS**: Convertir a mayúsculas y pegar
- **minúsculas**: Convertir a minúsculas y pegar
- **Título**: Capitalizar palabras y pegar

**Formato:**
- **Limpiar Formato**: Elimina espacios extra y caracteres especiales
- **Unir Líneas**: Elimina saltos de línea
- **Entrecomillar**: Agrega comillas alrededor del texto

**Extracción:**
- **Extraer Enlaces**: Todos los URLs del texto
- **Extraer Emails**: Direcciones de correo
- **Extraer Números**: Todos los números
- **Convertir a CSV**: Tabla de texto a formato CSV

**Uso:**
1. Copia texto al portapapeles
2. Abre Stalker con hotkey
3. Escribe `/actions`
4. Selecciona la acción deseada

---

## Uso y Comandos

### Hotkey Global

Por defecto: **Ctrl+Space** (configurable en Settings)

### Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `app nombre` | Buscar y abrir aplicación |
| `calc 2+2` | Calcular expresión |
| `/files query` | Buscar archivos |
| `/clipboard` | Historial portapapeles |
| `/snippets` | Gestionar snippets |
| `@trigger` | Expandir snippet |
| `/notes` | Buscar notas |
| `/links` | Enlaces rápidos |
| `/macros` | Macros grabadas |
| `/syshealth` | Monitor de sistema |
| `/overlay` | Toggle overlay |
| `/ai prompt` | Preguntar a IA |
| `/context` | Acciones contextuales |
| `/actions` | Acciones sobre portapapeles |
| `>config` | Configuración |

### Atajos de Teclado

- **Enter**: Ejecutar acción seleccionada
- **Ctrl+C**: Copiar texto de resultado
- **Ctrl+W**: (en /syshealth) Terminar proceso
- **Escape**: Cerrar launcher

---

## Guía de Automatización

### Crear Perfil Contextual Personalizado

1. **Identificar la aplicación:**
   - Abre la app
   - Usa `/context` en Stalker
   - Anota el nombre del proceso y clase de ventana

2. **Crear archivo de perfil:**
   - Ubicación: `~/.stalker/profiles/myapp.json`

3. **Definir acciones:**
```json
{
  "app_name": "myapp",
  "display_name": "Mi Aplicación",
  "window_class": "WindowClass",
  "window_title_pattern": "App Title.*",
  "actions": [
    {
      "name": "mi_accion",
      "description": "Mi acción personalizada",
      "trigger": "ctrl+shift+x",
      "action_type": "flow",
      "action_data": {"flow": "my_custom_flow"}
    }
  ],
  "snippets": {
    "@sigla": "Texto expandido completo"
  }
}
```

### Crear Flow Command Personalizado

1. **Planear pasos:**
   - ¿Qué teclas presionar?
   - ¿Qué comandos ejecutar?
   - ¿Qué datos transformar?

2. **Crear archivo de flow:**
   - Ubicación: `~/.stalker/flows/myflow.json`

3. **Ejemplo - Convertir selección a mayúsculas:**
```json
{
  "name": "to_uppercase",
  "description": "Convertir selección a mayúsculas",
  "app_context": "any",
  "steps": [
    {
      "action": "keystroke",
      "params": {"keys": "ctrl+c"}
    },
    {
      "action": "wait",
      "params": {"duration": 0.3}
    },
    {
      "action": "clipboard",
      "params": {"operation": "get"}
    },
    {
      "action": "transform",
      "params": {"type": "uppercase"}
    },
    {
      "action": "paste",
      "params": {"text": "${transformed_text}"}
    }
  ]
}
```

### Casos de Uso Comunes

#### **Desarrollador Web**

**Perfiles útiles:**
- VSCode: acceso rápido a funciones
- Browser: guardar/restaurar sesiones
- Terminal: comandos frecuentes

**Snippets:**
- `@log` → `console.log()`
- `@func` → function template
- `@import` → import statement

**Flows:**
- Copiar ruta de archivo y abrir en editor
- Extraer enlaces de documentación
- Formatear código copiado

#### **Diseñador**

**Perfiles útiles:**
- Figma/Adobe: exportar selección
- Explorer: organizar archivos de proyecto

**Actions:**
- Limpiar nombres de archivo
- Convertir rutas a formato portable
- Comprimir y compartir assets

#### **Escritor/Blogger**

**Perfiles útiles:**
- Word/Editor: snippets de formato
- Browser: guardar research

**Actions:**
- Limpiar formato de texto copiado
- Extraer enlaces de artículos
- Convertir tablas a Markdown

---

## Configuración

### Panel de Configuración

Acceso: `>config` o `/settings`

**Secciones:**

1. **General**
   - Hotkey global
   - Autostart con Windows
   - Tema (claro/oscuro)
   - Color de acento

2. **Interfaz**
   - Fuente y tamaño
   - Opacidad (activa/inactiva)
   - Efectos visuales

3. **Módulos**
   - Habilitar/deshabilitar:
     - Portapapeles
     - Snippets
     - Archivos
     - Enlaces
     - Macros
     - IA
     - Optimizer/SysHealth

4. **Rendimiento**
   - Modo de bajo consumo
   - Pausar indexador
   - Desactivar efectos

5. **IA**
   - Provider (OpenAI/Azure/Gemini)
   - API Key
   - Modelo
   - Parámetros (temperatura, max_tokens)

6. **SysHealth**
   - Intervalo de actualización
   - Overlay habilitado
   - Posición del overlay
   - Transparencia

### Archivos de Configuración

**Ubicaciones:**
- Configuración principal: `~/.fastlauncher/config.json`
- Perfiles contextuales: `~/.stalker/profiles/`
- Flow commands: `~/.stalker/flows/`
- Base de datos: `~/.fastlauncher/launcher.db`

---

## Solución de Problemas

### Stalker no responde al hotkey

1. Verificar que no hay conflicto con otro programa
2. Cambiar hotkey en Settings
3. Reiniciar Stalker

### Indexador de archivos es lento

1. Activar Modo de Rendimiento
2. Reducir drives indexados en configuración
3. Pausar indexador temporalmente

### IA no responde

1. Verificar API Key en Settings > AI
2. Comprobar conexión a internet
3. Verificar límites de uso de la API

### Snippets no se expanden

1. Verificar trigger está configurado
2. Comprobar que el módulo de snippets está activo
3. Verificar no hay conflicto con otra app

### Acciones contextuales no aparecen

1. Verificar que la ventana activa está detectada
2. Usar `/context` para ver información de detección
3. Crear perfil personalizado si es necesario

### Flow Command no funciona

1. Verificar sintaxis JSON
2. Comprobar que las acciones son válidas
3. Agregar `wait` entre pasos si es necesario
4. Verificar variables están correctamente referenciadas

---

## Arquitectura del Sistema

### Módulos Principales

**Core:**
- `app.py`: Aplicación principal, manejo del ciclo de vida
- `engine.py`: Motor de búsqueda, integración de módulos
- `config.py`: Gestión de configuración
- `storage.py`: Base de datos SQLite
- `intent_router.py`: Detección de intenciones local
- `compound_actions.py`: Gestión de acciones compuestas
- `context_profiles.py`: Perfiles por aplicación
- `flow_commands.py`: DSL y ejecución de flows

**Modules:**
- `calculator.py`: Evaluación de expresiones matemáticas
- `clipboard_manager.py`: Monitoreo y historial
- `snippet_manager.py`: Expansión de snippets
- `file_indexer.py`: Indexación de archivos
- `app_launcher.py`: Búsqueda y lanzamiento de apps
- `quicklinks.py`: Enlaces rápidos
- `macro_recorder.py`: Grabación y reproducción
- `notes.py`: Sistema de notas Markdown
- `ai_assistant.py`: Integración con IA
- `syshealth.py`: Monitor de sistema
- `window_manager.py`: Gestión de ventanas, detección de contexto
- `contextual_actions.py`: Acciones rápidas contextuales

**UI:**
- `launcher.py`: Ventana principal de búsqueda
- `settings_panel.py`: Panel de configuración
- `notes_editor.py`: Editor de notas
- `ai_response_panel.py`: Panel de respuestas de IA
- `syshealth_overlay.py`: Overlay del monitor

### Flujo de Datos

1. **Usuario presiona hotkey** → `hotkey.py` detecta
2. **Ventana se muestra** → `launcher.py`
3. **Usuario escribe query** → `search.py` (debounce)
4. **Motor procesa** → `engine.py`:
   - Detecta intención → `intent_router.py`
   - Busca en módulos activos
   - Aplica scoring
   - Detecta contexto → `window_manager.py`
   - Sugiere acciones → `compound_actions.py`
5. **Resultados se muestran** → `launcher.py`
6. **Usuario selecciona** → Ejecuta acción correspondiente

---

## Privacidad y Seguridad

### Procesamiento Local

- ✅ Intent Router funciona 100% offline
- ✅ Compound Actions no envían datos a la nube
- ✅ Context Profiles se almacenan localmente
- ✅ Flow Commands se ejecutan en el dispositivo

### Datos Sensibles

- Notas encriptadas con AES-256
- API keys almacenadas con protección de Windows DPAPI
- Historial de portapapeles local (no se sincroniza)
- Base de datos SQLite protegida

### IA Opcional

- BYOK: traes tu propia API key
- No se almacenan conversaciones sin consentimiento
- Se puede deshabilitar completamente

---

## Contribuir y Extender

### Agregar Nuevo Módulo

1. Crear archivo en `/modules/`
2. Implementar interfaz de búsqueda si aplica
3. Registrar en `engine.py`
4. Agregar comando en `internal_commands`

### Crear Intent Type

1. Agregar en `IntentType` enum (`intent_router.py`)
2. Definir patterns de detección
3. Agregar lógica en `detect_intent()`
4. Implementar sugerencias en `_intent_suggestions()`

### Extender Context Profiles

1. Crear perfil JSON en `~/.stalker/profiles/`
2. Definir acciones y snippets
3. Opcionalmente: agregar perfil builtin en `context_profiles.py`

---

## Rendimiento

### Optimizaciones Implementadas

- Debounce en búsqueda (250ms)
- Indexación de archivos en background thread
- Cache de resultados frecuentes
- Modo de bajo consumo
- Lazy loading de módulos pesados

### Benchmarks Típicos

- Tiempo de respuesta search: < 50ms
- Expansión de snippet: < 10ms
- Detección de intención: < 5ms
- Apertura de launcher: < 100ms

---

## Licencia y Créditos

**Proyecto:** Stalker - Advanced Windows Launcher
**Autor:** moltenisoy
**Licencia:** Ver LICENSE file

**Tecnologías utilizadas:**
- PySide6 (Qt for Python)
- SQLite
- Python 3.12+
- pywin32
- keyboard/mouse libraries

---

## Roadmap Futuro

### Planificado

- [ ] Integración con más aplicaciones
- [ ] Plugin system para extensiones de terceros
- [ ] Sincronización cloud opcional (E2E encrypted)
- [ ] Templates de Flow Commands compartibles
- [ ] Machine learning para sugerencias personalizadas
- [ ] Soporte multiidioma mejorado
- [ ] Gestos con mouse/touchpad
- [ ] Modo portable (USB)

---

## Contacto y Soporte

**Issues:** [GitHub Issues](https://github.com/moltenisoy/stalker/issues)
**Documentación adicional:** `/docs/`
**Ejemplos de flows:** `/examples/` (próximamente)

---

*Documentación actualizada: 2025-01-07*
*Versión: 2.0 (Intent Router + Context Profiles)*
