import re
import setuptools  # type: ignore


with open('toppy/__init__.py', 'r') as v:
    version = re.search(
        r"'?__version__'? = '?\d\.\d\.\d'?",
        v.read()
    ).group().replace("'", '')  # type: ignore
    version = version[version.index('=')+2:]


with open('requirements.txt', 'r') as r:
    requirements = r.read().splitlines()


with open('README.rst', 'r') as rm:
    readme = rm.read()


extras_require = {
    'cache': [
        'aiosqlite',
        'aiofiles'
    ]
}


packages = [
    'toppy',
    'toppy.webhook'
]


setuptools.setup(
    name='toppy-python',
    author='The Master',
    version=version,
    packages=packages,
    license='MIT',
    description='A simple API wrapper for Discord Bot List, DiscordBotsGG, and Top.gg',
    project_urls={
        "Documentation": "https://toppy-python.readthedocs.io/en/latest/",
        "Github": "https://github.com/chawkk6404/toppy",
    },
    long_description=readme,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
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
