#!/usr/bin/env python

# from distutils.core import setup, Extension
from setuptools import setup, command
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
os.environ["CC"] = "c++" 
os.environ["CXX"] = "c++"

required_packages=read('requirements.txt').split()

# # Common flags for both release and debug builds.
# extra_compile_args = sysconfig.get_config_var('CFLAGS').split()
# extra_compile_args += ["-std=c++11", "-Wall", "-Wextra"]
# if _DEBUG:
#     extra_compile_args += ["-g3", "-O0", "-DDEBUG=%s" % _DEBUG_LEVEL, "-UNDEBUG"]
# else:
#     extra_compile_args += ["-DNDEBUG", "-O3"]
    
    
#     libraries=['CPEDS','Mscscore','Mscsfn','hdf5'],
# cpedsRotation = Extension(
#     'pyCPEDScommonFunctions/cpedsRotation',
#     sources=['pyCPEDScommonFunctions/cpedsRotation.cpp'],
#     include_dirs=['/usr/local/include/cpems', '/usr/lib64/python2.7/site-packages/numpy/core/include/numpy'],
#     library_dirs=['/usr/local/lib/cpems'],
#     libraries=['nova',  'gsl', 'gslcblas', 'm', 'proj', 
#                'QtCore', 'fftw3', 'fftw3l', 'hdf5', 'CGAL', 'gmp','cfitsio', 'CPEDS', 'Mscsfn', 
#                'Mscscore', 'Mscsplot', 'MscsWMAP', 'armadillo', 
#                'gsl', 'gslcblas', 'm', 'proj', 'QtCore', 'fftw3', 'ccSHT3', 'novas', 'velKB', 'slaRefr', 
#                'fftw3l', 'hdf5', 'CGAL', 'gmp', 'cfitsio', 'cpgplot', 'armadillo'],
#     language='C++',
#     )

setup(name='RT32netlog',
      version='1.2.0',
      description='Capture and store UDP datagrams',
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      author='Bartosz Lew',
      author_email='bartosz.lew@umk.pl',
      url='',
      install_requires=required_packages,      
      package_dir = {'': 'python'},
      packages = ['RT32logging',
                  'RT32logging/communication',
                  'RT32logging/database',
                  'RT32logging/common',
                  ],
      scripts=['python/services/save-UDPdata-generic-module.py',
               ],
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License"
        ],
     )
      #       ext_modules=[cpedsRotation]

#       py_modules = ['pyCPEDScommonFunctions.libcpedsRotation.so'],
#       py_modules=['RadiometerData.RPG_tau','RadiometerData.RPG_Tatm'],


