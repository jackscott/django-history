from setuptools import setup, find_packages

setup(
    name='django_history',
    version='0.1.0',
    description='',
    long_description=open('README.rst').read(),
    author='Jack Scott',
    author_email='js@nine78.com',
    packages=find_packages(exclude=('tests', 'example')),
    install_requires=[
        'django>=1.4.2,<1.7',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
