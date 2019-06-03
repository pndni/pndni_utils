from setuptools import setup, find_packages


setup(
    name='pndni_utils',
    version='dev',
    packages=find_packages('python'),
    package_dir={'': 'python'},
    install_requires=[
        'pandas>=0.24',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fscombine = pndni.freesurfer:combine_stats_cmd',
        ],
    },
)
