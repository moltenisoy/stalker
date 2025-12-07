# Icon Guide for Stalker

This guide explains how to create and use a custom icon for the Stalker executable.

## Icon Requirements

### File Format
- **Format**: Windows Icon (`.ico`)
- **Required**: Yes (for professional appearance)
- **Optional**: Build works without icon, uses default

### Recommended Sizes
Include multiple resolutions in a single `.ico` file:
- 16x16 pixels (small taskbar)
- 32x32 pixels (standard taskbar)
- 48x48 pixels (large icons view)
- 64x64 pixels (extra large icons)
- 128x128 pixels (jumbo icons)
- 256x256 pixels (highest quality)

### Color Depth
- 32-bit color (with alpha channel for transparency)
- 24-bit color (minimum)

## Creating an Icon

### Option 1: Online Icon Converter
Convert an existing image to `.ico` format:

1. **ConvertICO** (https://convertico.com/)
   - Upload PNG/JPG
   - Select multiple sizes
   - Download `.ico` file

2. **ICO Convert** (https://icoconvert.com/)
   - Upload image
   - Choose sizes: 16, 32, 48, 64, 128, 256
   - Download result

### Option 2: Professional Design Tools

#### Adobe Photoshop
1. Install ICO plugin
2. Create 256x256 image
3. Save As → Windows Icon (*.ico)

#### GIMP (Free)
1. Create 256x256 image
2. Export As → Microsoft Windows Icon (*.ico)
3. Select multiple sizes when exporting

#### Inkscape (Free, Vector)
1. Create vector design
2. Export as PNG (256x256)
3. Convert to ICO using online tool

### Option 3: Icon Design Websites
Professional icon creation:

- **Figma** (https://figma.com/) - Free tier available
- **Canva** (https://canva.com/) - Icon templates
- **IconFinder** (https://iconfinder.com/) - Download existing icons

## Design Guidelines

### Visual Style
- **Simplicity**: Clear and recognizable at small sizes
- **Contrast**: Works well on both light and dark backgrounds
- **Consistency**: Matches app's branding and theme

### Colors
- Use brand colors (if applicable)
- Consider Windows taskbar background
- Ensure visibility at 16x16 size

### Content
- Avoid text (illegible at small sizes)
- Use simple, bold shapes
- Maximize use of space
- Leave small padding around edges

## Example Design Concepts for Stalker

### Concept 1: Eye/Vision
- Represents "stalking" or monitoring
- Modern, minimalist eye icon
- Blue/purple gradient

### Concept 2: Crosshair/Target
- Represents precision and focus
- Clean geometric design
- Accent color from theme

### Concept 3: Lightning Bolt
- Represents speed and power
- Simple, recognizable shape
- High contrast

### Concept 4: Abstract 'S' Letter
- First letter of Stalker
- Stylized, modern typography
- Integrated with geometric shape

## Using Your Icon

### With Build Script
Place your icon file in the project root and run:

```bash
python build_exe.py --icon stalker.ico
```

Or specify full path:

```bash
python build_exe.py --icon "C:\path\to\icon.ico"
```

### Manual PyInstaller
```bash
pyinstaller --icon=stalker.ico ... main.py
```

### Verifying Icon
After building:
1. Check `Stalker.exe` in Windows Explorer
2. Icon should appear on the file
3. Right-click → Properties → should show custom icon
4. Pin to taskbar → should show custom icon

## Default Behavior (No Icon)

If no icon is provided:
- Build succeeds with warning message
- Executable uses Python/PyInstaller default icon
- Functionality unaffected
- Can add icon later with resource editor

## Adding Icon to Existing EXE

If you built without icon, you can add one later:

### Using Resource Hacker (Free)
1. Download Resource Hacker (http://angusj.com/resourcehacker/)
2. Open `Stalker.exe`
3. Action → Add from file
4. Select your `.ico` file
5. Save the executable

### Using Visual Studio (If Available)
1. Open VS Command Prompt
2. Use `editbin` or resource editor
3. Add icon resource

## Testing Your Icon

### Checklist
- [ ] Icon appears in Windows Explorer
- [ ] Icon visible at 16x16 (Small icons)
- [ ] Icon visible at 32x32 (Medium icons)
- [ ] Icon visible at 48x48 (Large icons)
- [ ] Icon visible at 256x256 (Extra large icons)
- [ ] Icon appears when pinned to taskbar
- [ ] Icon appears in Alt+Tab switcher
- [ ] Icon appears in Task Manager
- [ ] Icon has transparent background (if needed)
- [ ] Colors work on light and dark backgrounds

## Troubleshooting

### Icon Not Appearing
1. **Clear icon cache**:
   ```cmd
   ie4uinit.exe -show
   ```
   Or restart Windows Explorer

2. **Verify .ico file**: Open with image viewer to check all sizes included

3. **Rebuild**: Clean build directory and rebuild
   ```bash
   python build_exe.py --icon stalker.ico
   ```

### Icon Looks Pixelated
- Include higher resolution versions (128x128, 256x256)
- Use vector source and export at multiple sizes
- Ensure 32-bit color depth

### Wrong Icon Appearing
- Clear Windows icon cache
- Delete `build/` and `dist/` folders
- Rebuild from scratch

## Sample Icon File Structure

A proper `.ico` file contains multiple images:
```
stalker.ico
├── 16x16 @ 32bpp
├── 32x32 @ 32bpp
├── 48x48 @ 32bpp
├── 64x64 @ 32bpp
├── 128x128 @ 32bpp
└── 256x256 @ 32bpp
```

You can verify this with `Resource Hacker` or online ico analyzers.

## Free Icon Resources

### Icon Downloads (Check Licenses)
- **Flaticon** (https://flaticon.com/) - Mostly free with attribution
- **Icons8** (https://icons8.com/) - Free with attribution
- **Feather Icons** (https://feathericons.com/) - MIT License
- **Material Icons** (https://material.io/icons/) - Apache License

### Icon Fonts (Convert to ICO)
- Font Awesome
- Material Design Icons
- Ionicons

**Note**: Always check license terms before using icons in distributed software.

## Best Practices

1. **Start with Vector**: Use SVG or AI format initially
2. **Export Multiple Sizes**: Don't just scale 256x256 down
3. **Optimize Each Size**: Adjust details for small sizes
4. **Test Early**: Build with icon early in development
5. **Match Brand**: Consistent with app's visual identity
6. **Keep Simple**: Works at all sizes
7. **Use Transparency**: Alpha channel for irregular shapes

## Additional Resources

- [Microsoft Icon Design Guidelines](https://docs.microsoft.com/en-us/windows/win32/uxguide/vis-icons)
- [PyInstaller Icon Documentation](https://pyinstaller.org/en/stable/usage.html#cmdoption-icon)
- [ICO File Format Specification](https://en.wikipedia.org/wiki/ICO_(file_format))
