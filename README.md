# CV parser for faculty database to enhance collaboration

This is still a work in progress, there are couple of items that have to be done.

## Project Overview

This project is aimed to create a faculty database to enhance collaboration and communication between faculty members.
The database will be used to create a faculty directory for faculty members to search for detailed information. To minimize
the burden on the faculty members, we are creating a CV parser to extract structured information from the CV pdf files. 

This will then be used to create a database with detailed information about the faculty members and other can search for 
experts in their fields to collaborate.

## The Database

In the backend we are using PostgreSQL database you can find the schema in the `database/tables.py` file. This defined
all the tables and their respective columns as well as the indices and relationships between the tables. 

The database class instance is just a simple wrapper around the database connection with other actively collected metadata
to make queries eaiser. 

## Querying the Database

** COMING SOON **

## Parser

This is the main workhorse of the project. It contains 2 modules `cv_structure` is a collection of dataclasses that defines
how a cv is supposed to be structured and `cv_parser` is the main module that parses the cv and extracts the structured data.

This is still a work in progress, and there are a few quirks that need to be fixed. Academic cvs can be very long and not 
perfectly structured or standardized. We are relying on U of T's guidelines to get sections from the CVs but not all cvs
have all the sections and not all sections are labelled in a standard way. To work around this isuse we are relying on font
sizes and font names that are present in the CV to find headers and subheaders. These are then used to classify the sections
into the `cv_structure` dataclass which are then extracted using whatever specific subsection is relavant to that chunk of the CV. 

This means that we:
1. Cannot use images to classify sections
2. Need standardized formatting (at least the headers need to be different font sizes that is larger than the subheaders)
3. The sections in the CV must have equivalent and corresponding sections that are described in the cv_structure dataclass

## Installation

This project is still in development and not yet published to PyPI. We are relying conda to collect all the python and non-python
dependencies. To install the package you will need to clone the repository with

```bash
git clone https://github.com/ccmbioinfo/cv_db
cd cv_db
```

After cloning the repository you can install the package with

```bash
conda env create -f environment.yaml
```

This will collect all the dependencies and create a conda environment called `cv_parser`. You will need to activate the environment
with

```bash
conda activate cv_parser
```

and then you can install the package with

```bash
pip install -e .`
```

Keep in mind that this is still a work in progress and the package can change substantially with many breaking changes.
that might make it incompatible with your current setup.

## Contributing

Please feel free to contribute to this project. For guidelines on how to contribute please see the `CONTRIBUTING.md` file.