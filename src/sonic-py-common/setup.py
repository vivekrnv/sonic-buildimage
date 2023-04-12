from setuptools import setup

dependencies = [
    'natsort==6.2.1', # 6.2.1 is the last version which supports Python 2
    'pyyaml',
    'redis-dump-load',
]

setup(
    name='sonic-py-common',
    version='1.0',
    description='Common Python libraries for SONiC',
    license='Apache 2.0',
    author='SONiC Team',
    author_email='linuxnetdev@microsoft.com',
    url='https://github.com/Azure/SONiC',
    maintainer='Joe LeVeque',
    maintainer_email='jolevequ@microsoft.com',
    install_requires=dependencies,
    packages=[
        'sonic_py_common',
    ],
    setup_requires= [
        'pytest-runner',
        'wheel'
    ],
    tests_require=[
        'pytest',
        'mock==3.0.5' # For python 2. Version >=4.0.0 drops support for py2
    ],
    entry_points={
        'console_scripts': [
            'sonic-db-load = sonic_py_common.sonic_db_dump_load:sonic_db_dump_load',
            'sonic-db-dump = sonic_py_common.sonic_db_dump_load:sonic_db_dump_load',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python',
    ],
    keywords='SONiC sonic PYTHON python COMMON common',
    test_suite = 'setup.get_test_suite'
)

