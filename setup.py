from setuptools import setup

setup(
    name='privacycow',
    version='0.0.2',
    py_modules=['privacycow'],
    install_requires=[
        'Click==8.0.1',
        'texttable==1.6.3',
        'requests==2.25.1',
    ],
    entry_points={
        'console_scripts': [
            'privacycow = privacycow:cli',
        ],
    },
)
