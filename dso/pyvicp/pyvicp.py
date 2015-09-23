from distutils.core import setup, Extension

module1 = Extension('vicp',
                    libraries = ['vicp'],
                    library_dirs = ['../libvicp/'],
                    sources = ['pyvicp.c'])

setup (name = 'vicp',
       version = '1.0',
       description = 'Python interface to VICP library',
       ext_modules = [module1])
