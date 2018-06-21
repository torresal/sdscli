from setuptools import setup, find_packages
import sdscli


setup(
    name='sdscli',
    version=sdscli.__version__,
    long_description=sdscli.__description__,
    url=sdscli.__url__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
<<<<<<< HEAD
    install_requires=[ 'distribute', 'pyyaml', 'pygments', 'prompt-toolkit==1.0.15', 
                       'fabric', 'tqdm==4.19.7', 'backoff' ],
=======
    install_requires=[ 'distribute', 'pyyaml', 'pygments', 
                       'prompt-toolkit>=1.0,<2.0', 'fabric', 
                       'tqdm==4.19.7', 'backoff' ],
>>>>>>> 06c278a8d8c6d3ad01dd9fd26f6f9607158f42ef
    entry_points={
        'console_scripts': [
            'sds=sdscli.command_line:main'
        ]
    },
    package_data={
        '': [ 'adapters/hysds/files/*', 'adapters/hysds/files/*/*',
              'adapters/sdskit/files/*', 'adapters/sdskit/files/*/*' ],
    }
)
