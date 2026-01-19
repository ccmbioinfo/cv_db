from setuptools import setup, find_packages

#TODO website under docs and github actions supporting them.

setup(
    name='cv_db',
    version='0.1.0',
    description="A cv parser and database for facilitating collaboration",
    author='Alper Celik',
    author_email='alper.celik@sickkids.ca',
    packages=find_packages(),
    zip_safe=False,
    package_data={"": ["*.json"]},
    include_package_data=True
)