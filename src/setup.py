from distutils.core import setup
import py2exe

setup(console=[{'script':'src/console.py','dest_base':'ns2update'}])
#setup(console=[{'script':'src/service.py','dest_base':'ns2updateservice'}])