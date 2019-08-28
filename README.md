Judicial Vacancy Data
=====================

The United States Courts maintain a [dataset on federal judicial vacancies](https://www.uscourts.gov/judges-judgeships/judicial-vacancies), including historic data in PDF and CSV. This repo will contain:

- A copy of the raw data files downloaded from US courts. (`raw/`)
- A tool for downloading the raw data files. (`judicial_data/download.py`)
- Tools for converting the raw data files in both the HTML and PDF formats.
- Results of the conversion process for each month. (`data/`)
- Manually input data for periods when automatic conversion is not possible.
- A tool for combining the data into one row per vacancy.