from distutils.core import setup


setup(
    name = "idios",
    version = "0.1.dev6",
    author = "Eldarion",
    author_email = "development@eldarion.com",
    description = "an extensible profile app designed to replace the profiles apps in Pinax",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/eldarion/idios",
    packages = [
        "idios",
        "idios.templatetags",
        "idios.tests",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
