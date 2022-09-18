from distutils.core import setup

setup(
    name='pywda',
    packages=['pywda'],
    version='0.1',
    license='MIT',
    install_requires=[
        'retry',
        'requests',
        'logzero'
    ])
