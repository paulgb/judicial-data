import pandas as pd

# In case of multiple tables in the HTML file, the one containing this string will be extracted.
MATCH_STRING = 'Incumbent'

def parse_html(html_path):
    result, = pd.read_html(html_path, header=1, match=MATCH_STRING)
    return result
