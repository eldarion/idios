from setuptools import find_packages, setup


setup(
    name="idios",
    version=__import__("idios").__version__,
    author="Eldarion",
    author_email="development@eldarion.com",
    description="an extensible profile app designed to replace the profiles apps in Pinax",
    long_description=open("README.rst").read(),
    license="BSD",
    url="http://github.com/eldarion/idios",
    install_requires=[
        "Django>=1.6.5",
        "django-appconf>=0.6",
        "django-user-accounts>=1.0c9"
    ],
    tests_require=[
        "Django>=1.6.5",
        "django-appconf>=0.6",
        "django-user-accounts>=1.0c9",
    ],
    test_suite="runtests.runtests",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
