# SecureFace.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['C:/Users/sanso/Desktop/Project/SecureFace-NE-main'],
    binaries=[],
    datas=[
        ('C:/Users/sanso/Desktop/Project/SecureFace-NE-main/SetUp/mensaje.png', 'SetUp'),
        ('C:/Users/sanso/Desktop/Project/SecureFace-NE-main/DataBase/Users/*', 'DataBase/Users'),
        ('C:/Users/sanso/Desktop/Project/SecureFace-NE-main/DataBase/Faces/*', 'DataBase/Faces'),
        # Añadir el archivo de datos necesario
        ('C:/ruta/a/tu/archivo/shape_predictor_68_face_landmarks.dat', 'face_recognition_models/models')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SecureFace',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Cambia a True si quieres ver la consola
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SecureFace',
)
