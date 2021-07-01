from setuptools import setup

setup(
    name='privacycow',
    version='0.0.2',
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
