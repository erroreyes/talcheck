import setuptools
from setuptools import setup

setup(
    name = "talcheck",
    version = "1.0.0",
    packages = setuptools.find_packages(include=["talcheck"]),
    scripts = ["talcheck.py"],
    description = "Check for new version of TAL plugins.",
    author = "roby",
    author_email = "rbrgsnvs@gmail.com",
    install_requires = [
        "urllib3", 
        "dateparser"
    ],
    include_package_data = True,
    package_data={'talcheck': ['data/data.json']},
)
