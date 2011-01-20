from setuptools import setup, find_packages
import os

version = '0.1'
shortdesc ="runtime engine for node.ext.uml based activities"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()

setup(name='activities',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
      ], # Get strings from http://www.python.org/pypi?:action=list_classifiers
      keywords='',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url='http://github.com/bluedynamics/activities',
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['activities'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'node.ext.uml',
          'zope.interface',
          'zope.component',
      ],
      extras_require={
          'test': [
              'interlude',
              'zope.configuration',
          ]
      },
      entry_points="""
      [console_scripts]
      """,
      )

