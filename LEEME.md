# Stalker - Guía de Instalación y Uso (Windows)

## 🚀 Instalación Rápida

### Opción 1: Usar el ejecutable (Recomendado)

1. Descarga `Stalker.exe` desde la sección de [Releases](https://github.com/moltenisoy/stalker/releases)
2. Ejecuta `Stalker.exe`
3. La primera vez, se creará la configuración automáticamente en `%USERPROFILE%\.fastlauncher\`

### Opción 2: Ejecutar desde el código fuente

#### Paso 1: Instalar Python

1. Descarga Python 3.9 o superior desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, **asegúrate de marcar "Add Python to PATH"**
3. Verifica la instalación abriendo CMD y escribiendo:
   ```cmd
   python --version
   ```

#### Paso 2: Instalar dependencias

**Método automático (recomendado):**

Simplemente haz doble clic en `install.bat` - este script instalará todas las dependencias automáticamente.

**Método manual:**

Abre CMD en la carpeta del proyecto y ejecuta:
```cmd
pip install -r requirements.txt
```

#### Paso 3: Ejecutar la aplicación

```cmd
python main.py
```

## 🔧 Crear el ejecutable (.exe)

Si quieres crear tu propio ejecutable:

1. Instala PyInstaller:
   ```cmd
   pip install -r requirements-build.txt
   ```

2. Ejecuta el script de compilación:
   ```cmd
   python build_exe.py
   ```

3. El ejecutable se creará en la carpeta `dist/`

## ⌨️ Uso Básico

### Hotkey Global

Presiona **`Ctrl+Space`** en cualquier momento para abrir/cerrar el lanzador.

### Comandos Básicos

- **Abrir aplicaciones**: Escribe el nombre (ej: `chrome`, `notepad`)
- **Buscar archivos**: `/files nombre_archivo`
- **Historial del portapapeles**: `/clipboard`
- **Snippets de texto**: `/snippets`
- **Calculadora**: Escribe directamente (ej: `2+2`, `sqrt(16)`)
- **Monitor del sistema**: `/syshealth`
- **Notas**: `/notes`
- **Configuración**: `>config` o `settings`

## 🐛 Solución de Problemas

### El ejecutable se cierra inmediatamente

**Posibles causas:**
1. Falta Microsoft Visual C++ Redistributable
2. Problema con la configuración

**Soluciones:**
- Descarga e instala [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Elimina la carpeta `%USERPROFILE%\.fastlauncher\` y vuelve a ejecutar
- Revisa los logs en `%USERPROFILE%\.fastlauncher\logs\app.log`

### El programa no inicia desde Python

**Verifica las dependencias:**
```cmd
python test_imports.py
```

Si hay errores, reinstala las dependencias:
```cmd
pip install -r requirements.txt --force-reinstall
```

### El hotkey no funciona

1. Verifica que otra aplicación no esté usando `Ctrl+Space`
2. Abre configuración (`>config`) y cambia el hotkey
3. Ejecuta como Administrador si es necesario

### Errores de importación

Asegúrate de que estás ejecutando desde la carpeta raíz del proyecto:
```cmd
cd C:\ruta\a\stalker
python main.py
```

## 📝 Configuración

La configuración se encuentra en: `%USERPROFILE%\.fastlauncher\config.json`

Puedes editarla manualmente o usar el panel de configuración dentro de la aplicación.

### Ejemplo de configuración:

```json
{
  "hotkey": "ctrl+space",
  "ui": {
    "theme": "dark",
    "font_size": 11,
    "accent": "#3a86ff"
  },
  "modules": {
    "optimizer": true,
    "clipboard": true,
    "files": true,
    "ai": true
  }
}
```

## 💡 Consejos

1. **Primera ejecución**: La aplicación puede tardar unos segundos en indexar archivos
2. **Rendimiento**: Activa el modo de rendimiento en configuración si tu PC es lenta
3. **Búsqueda de archivos**: Configura las carpetas a indexar en configuración
4. **AI Assistant**: Necesitas tu propia API key (OpenAI o Anthropic)

## 📧 Soporte

- **Problemas**: Abre un issue en [GitHub Issues](https://github.com/moltenisoy/stalker/issues)
- **Documentación completa**: Ver [README.md](README.md) (inglés)
- **Logs**: Revisa `%USERPROFILE%\.fastlauncher\logs\app.log` para detalles de errores

---

**Nota**: Este proyecto está diseñado exclusivamente para Windows 10/11.
