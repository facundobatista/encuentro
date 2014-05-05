# -*- mode: python -*-
a = Analysis(['c:\\encuentro\\bin\\encuentro'],
             pathex=['C:\\pyinst', 'C:\\encuentro'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\encuentro', 'encuentro.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon='C:\\encuentro\\windows\\imgs\\encuentro.ico')
coll = COLLECT(exe,
               Tree('C:\\encuentro\\encuentro\\logos'),
               Tree('C:\\encuentro\\encuentro\\ui\\media'),
               a.binaries,
               a.zipfiles,
               a.datas + [
                   ('version.txt', 'C:\\encuentro\\version.txt', 'DATA')
               ],
               strip=None,
               upx=True,
               name=os.path.join('dist', 'encuentro'))
