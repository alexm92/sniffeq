from distutils.core import setup
from setuptools import find_packages


install_requires = [
    'pip',
    'pymongo==2.8',
    'mongoengine==0.8.7',
]

setup(
    name='sniffeq',
    version='0.0.1',
    description='Sniff equities',
    author='AlexM',
    packages=find_packages(),
    install_requires=install_requires,
    data_files=[
        ('/usr/bin', [
            'sys/bin/sniffeqserver',
            'sys/bin/sniffeqshell'
        ])
    ],
)
