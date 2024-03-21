from setuptools import setup
from Cython.Build import cythonize

# python cython_compile.py build_ext --inplace

setup(
    ext_modules = cythonize('decoding_utils_cython.pyx')
)