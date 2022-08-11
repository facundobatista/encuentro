# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['encuentro\\__main__.py'],
             pathex=['Z:\\encuentro'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='__main__',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='windows\\imgs\\encuentro.ico')
coll = COLLECT(exe,
               Tree('encuentro\\logos'),
               Tree('encuentro\\ui\\media'),
               a.binaries,
               a.zipfiles,
               a.datas + [
                   ('version.txt', 'encuentro\\version.txt', 'DATA'),
                   ('ffmpeg.exe', 'ffmpeg.exe', 'DATA'),
               ],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='__main__')
