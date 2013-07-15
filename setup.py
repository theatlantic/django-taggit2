import os
from setuptools import setup, find_packages


f = open(os.path.join(os.path.dirname(__file__), 'README.txt'))
readme = f.read()
f.close()

setup(
    name='django-taggit2',
    version=__import__('taggit').__version__,
    description='Reusable tagging with pluggable automatic tag generation',
    long_description=readme,
    author='The Atlantic',
    author_email='atmoprogrammers@theatlantic.com',
    url='http://github.com/theatlantic/django-taggit2/tree/master',
    packages=find_packages(),
    zip_safe=False,
    package_data = {
        'taggit': [
            'locale/*/LC_MESSAGES/*',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    test_suite='taggit.tests.runtests.runtests'
)

