import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="germ",
    version="1.0",
    install_requires=[
        "Django>=4.2.7",
        "django-filter>=23.5",
        "celery>=5.3.6",
        "django-celery-beat>=2.5.0",
        "redis>=5.0.1",
        "lxml>=5.2.1",
        "ezodf>=0.3.2",
        "python-dotenv>=1.0.1",
        "requests>=2.31.0",
    ],
    author="Henri Dewilde",
    description="Un projet django permettant de gérer la reservation et l'emprunt de matériel au sein d'une mutuelle d'outils.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bvr4/gestion-emprunt-et-reservation-materiel",
    project_urls={
        "Bug Tracker": "https://github.com/Bvr4/gestion-emprunt-et-reservation-materiel/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.8.10",
    scripts=["manage.py"],
)
