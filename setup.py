from setuptools import setup, find_packages

setup(name='django-bootstrap',
    version='0.1.0',
    license='MIT',
    description='Django starter kit',
    long_description='Starter kit',
    author='Lucas Tan',
    author_email='do-not-spam@gmail.com',
    url='http://github.com/lucastan/django-bootstrap',
    packages=find_packages(exclude=('djdemo',)),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
