from setuptools import setup

setup(name='inlined_calls_explorer',
      version='0.1',
      description='tool to track calls (esp, if there are many small ones)',
      url='http://github.com/dz0/inlined_calls_explorer',
      author='Jurgis Pralgauskis',
      author_email='Jurgis.Pralgauskis@gmail.com',
      license='MIT',
      packages=['funniest'],
      zip_safe=False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',

        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Debuggers',
    ],
      
      )
