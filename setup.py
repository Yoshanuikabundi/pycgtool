from setuptools import setup, find_packages

CLASSIFIERS = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 5 - Production/Stable',

    # Indicate who your project is intended for
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering :: Chemistry',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6'
]

setup(
    name='PyCGTOOL',
    version='1.0.0.post3',
    url='https://github.com/jag1g13/pycgtool',
    license='GPLv3',
    author='James Graham',
    author_email='J.A.Graham@soton.ac.uk',
    description='Automated generation of parameters for coarse-grained molecular dynamics simulation',
    entry_points={'console_scripts': ['pycgtool.py=pycgtool.__main__:main']},
    packages=find_packages(exclude=['test']),
    classifiers=CLASSIFIERS,
    keywords='molecular dynamics',

    test_suite='test',

    install_requires=['numpy', 'simpletraj'],
    extras_require={
        'mdtraj': ['cython', 'scipy', 'mdtraj'],
        'numba': ['cython', 'numba'],
        'test': ['pytest', 'coverage'],
        'full': ['scipy', 'mdtraj', 'cython', 'numba', 'pytest', 'coverage']
    }

    # data_files=[('pycgtool_data', [])]
)
