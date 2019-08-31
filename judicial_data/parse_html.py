import pandas as pd

# In case of multiple tables in the HTML file, the one containing this string
# will be extracted.
MATCH_STRING = 'Incumbent'

COLUMNS = [
    'Court',
    'Incumbent',
    'Vacancy Reason',
    'Vacancy Date',
    'Nominee',
    'Nomination Date',
]


def parse_html(html_path: str):
    result, = pd.read_html(html_path, header=None, match=MATCH_STRING)
    if result.columns[0] != 'Court':
        result, = pd.read_html(html_path, header=1, match=MATCH_STRING)

    result.columns = COLUMNS

    return result
