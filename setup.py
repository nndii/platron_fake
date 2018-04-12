from setuptools import setup

setup(
    name='platron_fake',
    version='1.0',
    description='',
    classifiers=[
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
    ],
    author='Andrey Maksimov',
    author_email='nndii@national.shitposting.agency',
    url='https://github.com/nndii/platron_fake',
    keywords=['ticketscloud', 'platron'],
    packages=['platron_fake'],
    install_requires=['aiohttp', 'requests'],
)
