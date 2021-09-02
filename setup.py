from setuptools import setup

setup(
    name='privacycow',
    version='0.0.4',
    py_modules=['privacycow'],
    install_requires=[
        'Click==8.0.1',
        'texttable==1.6.4',
        'requests==2.26.0',
    ],
    entry_points={
        'console_scripts': [
            'privacycow = privacycow:cli',
        ],
    },
)
