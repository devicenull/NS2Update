from distutils.core import setup
import py2exe

setup(windows=[{'script':'src/console.py','dest_base':'ns2update'}])