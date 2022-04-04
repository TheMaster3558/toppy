import re
import setuptools


with open('toppy/__init__.py', 'r') as v:
    version = re.search(
        "'?__version__'? = '?\d\.\d\.\d'?",
        v.read()
    ).group().replace("'", '')
    version = version[version.index('=')+1:]


with open('requirements.txt', 'r') as r:
    requirements = r.read().splitlines()


with open('README.md', 'r') as rm:
    readme = rm.read()


packages = [
    'toppy'
]


setuptools.setup(
    name='toppy',
    author='The Master',
    version=version,
    packages=packages,
    license='MIT',
    description='A simple API wrapper for Top.gg',
    url='https://github.com/chawkk6404/top_gg',
    long_description=readme,
    long_description_content_type='rst',
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.8.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
    ]
)




