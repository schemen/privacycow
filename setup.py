from setuptools import setup

setup(
    name='privacycow',
    version='0.0.1',
    py_modules=['privacycow'],
    install_requires=[
        'Click',
        'texttable',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'privacycow = privacycow:cli',
        ],
    },
)
