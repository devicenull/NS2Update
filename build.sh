export PATH=$PATH:/c/Python27/

rm -f dist/console.exe dist/ns2update.exe

python pyinstaller-1.5.1/Makespec.py src/console.py --onefile
python pyinstaller-1.5.1/Build.py console.spec

mv dist/console.exe dist/ns2update.exe
