del dist\console.exe
rmdir /s /q dist-x86
rmdir /s /q build

mkdir -p dist-x86

CALL env.cmd

%PYTHON_X86% pyinstaller-1.5.1-x86/Build.py console.spec

move dist\console.exe dist-x86\ns2update.exe

pause