from setuptools import setup, find_packages


setup(
    name='pndni_utils',
    version='dev',
    packages=find_packages('python'),
    package_dir={'': 'python'},
    install_requires=[
        'pandas>=0.24',
        'nibabel>=2.4.0',
        'numpy>=1.16.3',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    extra_require={
        'doc': ['Sphinx', 'sphinx-argparse', 'sphinx-rtd-theme']
    }
    entry_points={
        'console_scripts': [
            'fscombine = pndni.fscombine:combine_stats_cmd',
            'mnclabel2niilabel = pndni.mnclabel2niilabel:main',
            'combinelabels = pndni.combinelabels:main',
            'labels2probmaps = pndni.labels2probmaps:main',
            'swaplabels = pndni.swaplabels:main',
            'flattenhtml = pndni.flattenhtml:main',
            'allequal = pndni.all_equal:main',
        ],
    },
)
