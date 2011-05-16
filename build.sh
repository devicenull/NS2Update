rm -rf dist/ dist_x64/
/d/Python27/python.exe src/setup.py py2exe
mv dist dist_x64
/d/Python27_x86/python.exe src/setup.py py2exe