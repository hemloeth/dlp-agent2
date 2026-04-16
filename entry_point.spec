# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, copy_metadata, collect_dynamic_libs

easyocr_datas = collect_data_files('easyocr')
easyocr_meta = copy_metadata('easyocr')
torch_meta = copy_metadata('torch')
torch_datas = collect_data_files('torch')
docx_meta = copy_metadata('python-docx')
openpyxl_meta = copy_metadata('openpyxl')

# Combine all datas
all_datas = [("dlp_agent", "dlp_agent")] + easyocr_datas + easyocr_meta + torch_meta + torch_datas + docx_meta + openpyxl_meta
all_binaries = collect_dynamic_libs('torch')

a = Analysis(
    ['entry_point.py'],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=[
        'easyocr',
        'easyocr.easyocr',
        'torch',
        'torchvision',
        'PIL',
        'PIL.Image',
        'cv2',
        'numpy',
        'scipy',
        'skimage',
        'yaml',
        'requests',
        'urllib3',
        'charset_normalizer',
        'docx',
        'PyPDF2',
        'openpyxl',
        'pptx',
        'click',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='entry_point',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
