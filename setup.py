from setuptools import setup

version = '0.1'

install_requires = [
    ]

setup_requires = [
    ]

setup(name='thinkhazard_common',
      version=version,
      description='ThinkHazard: Overcome Risk - Common module',
      long_description=open('README.rst').read(),
      url='https://github.com/GFDRR/thinkhazard_common',
      author='Camptocamp',
      author_email='info@camptocamp.com',
      packages=['thinkhazard_common'],
      zip_safe=False,
      install_requires=install_requires,
      setup_requires=setup_requires,
      )
