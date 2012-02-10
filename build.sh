
rm -f dist/console.exe dist/ns2update.exe

/c/Python27/python pyinstaller-1.5.1/Makespec.py src/console.py --onefile
/c/Python27/python pyinstaller-1.5.1/Build.py console.spec

mv dist/console.exe dist/ns2update.exe
