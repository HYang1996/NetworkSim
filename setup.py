
from distutils.core import setup
import setuptools
import codecs

with codecs.open("README.rst", encoding="utf-8-sig") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='NetworkSim',
    packages=['NetworkSim'],
    version='0.2.2',
    license='MIT',
    description='A WDM ring datacentre network simulator',
    long_description=LONG_DESCRIPTION,
    maintainer='Hongyi Yang',
    maintainer_email='zceehya@ucl.ac.uk',
    url='https://github.com/HYang1996/NetworkSim',
    download_url='https://github.com/HYang1996/NetworkSim/archive/refs/tags/0.2.2.tar.gz',
    install_requires=[            # I get to this in a second
        'pandas',
        'simpy',
        'tqdm',
        'scipy',
        'seaborn',
        'matplotlib',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Intended Audience :: Science/Research",
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        "Topic :: Scientific/Engineering",
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
