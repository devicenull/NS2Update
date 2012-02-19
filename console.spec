# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'src/console.py'],
             pathex=['c:\\Source\\NS2Update'], hookspath=['C:\\Source\\NS2Update\\hooks'], excludes=['urllib.parse'])
pyz = PYZ(a.pure)
exe = EXE( pyz,
          #Verbose: a.scripts + [('v', '', 'OPTION')],
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'console.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=True )
