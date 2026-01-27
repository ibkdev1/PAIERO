# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database', 'database'),
        ('reports', 'reports'),
        ('ui', 'ui'),
        ('business', 'business'),
        ('models', 'models'),
        ('config.py', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pandas',
        'openpyxl',
        'reportlab',
        'reportlab.lib.colors',
        'reportlab.lib.utils',
        'numpy',
        'numpy._core',
        'numpy._core._multiarray_umath',
        'PIL',
        'PIL.Image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unused PyQt6 modules to reduce size
        'PyQt6.QtNetwork',
        'PyQt6.QtWebEngine',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtBluetooth',
        'PyQt6.QtDBus',
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
        'PyQt6.QtPositioning',
        'PyQt6.QtSensors',
        'PyQt6.QtSerialPort',
        'PyQt6.QtTest',
        # Exclude unused heavy libraries
        'matplotlib',
        'scipy',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PAIERO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip debug symbols to reduce size
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# macOS app bundle
app = BUNDLE(
    exe,
    name='PAIERO.app',
    icon=None,
    bundle_identifier='com.abdc.paiero',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleName': 'PAIERO',
        'CFBundleDisplayName': 'PAIERO',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': '© 2026 ABDC. All rights reserved.',
    },
)
