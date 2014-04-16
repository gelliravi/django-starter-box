from setuptools import setup, find_packages

setup(name='django-starter-box',
    version='0.1.1',
    license='MIT',
    description='Django starter box',
    long_description='Starter box',
    author='Lucas Tan',
    author_email='do-not-spam@gmail.com',
    url='http://github.com/lucastan/django-starter-box',
    packages=find_packages(exclude=('djdemo',)),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
    zip_safe=False,
)
