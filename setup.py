import re
import setuptools


with open('top_gg/__init__.py', 'r') as v:
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
    'top_gg'
]


setuptools.setup(
    name='top_gg',
    author='The Master',
    version=version,
    packages=packages,
    license='MIT',
    description='A simple API wrapper for Top.gg',
    url='https://github.com/chawkk6404/top_gg',
    long_description=readme,
    long_description_content_type='md',
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.10.0'
)



