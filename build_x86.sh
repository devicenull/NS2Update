rm -f dist/console.exe dist/ns2update.exe
rm -rf dist-x86/ build/

mkdir -p dist-x86

#/c/Python27_x86/python pyinstaller-1.5.1-x86/Makespec.py src/console.py --onefile
/c/Python27_x86/python pyinstaller-1.5.1-x86/Build.py console.spec

mv dist/console.exe dist-x86/ns2update.exe
