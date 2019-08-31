import pandas as pd
from time import sleep
from os import path, makedirs, unlink
from urllib.request import urlretrieve, URLError
import json
from datetime import datetime

# First date for which data is available.
MIN_DATE = pd.Timestamp('1981-01-01')

# Seconds to pause to be a good server user.
PAUSE = 3

REPORT_PARTS = [
    'vacancies',
    'emergencies',
    'summary',
    'future',
    'confirmations',
]

# URL formats. We try them in order.
URL_FORMATS = [
    ('https://www.uscourts.gov/judges-judgeships/judicial-vacancies/'
     'archive-judicial-vacancies/{}/{}/pdf', 'pdf'),
    ('https://www.uscourts.gov/judges-judgeships/judicial-vacancies/'
     'archive-judicial-vacancies/{}/{}/html', 'html'),
    ('https://www.uscourts.gov/judges-judgeships/judicial-vacancies/'
     'archive-judicial-vacancies/{}/{}', 'html')
]

NO_DATA_STRING = '<p>Sorry, we do not have data for this table.<p>'


def download_data(begin: pd.Timestamp = MIN_DATE, end: pd.Timestamp = None):
    if end is None:
        end = pd.Timestamp.now()

    for d in pd.date_range(begin, end, freq='MS'):
        ym = d.strftime('%Y/%m')
        meta = {
            'date': ym,
            'accessed': datetime.now().isoformat(),
            'files': [],
        }

        dirname = d.strftime('raw/%Y_%m')

        meta_file = path.join(dirname, 'meta.json')
        if path.exists(meta_file):
            print(f'Skipping {ym} (already exists).')
            continue
        makedirs(dirname)
        print(dirname)

        for report_part in REPORT_PARTS:
            for url_format, extension in URL_FORMATS:
                filename = f'{report_part}.{extension}'
                url = url_format.format(ym, report_part)
                print(url)
                try:
                    filepath = path.join(dirname, filename)
                    urlretrieve(url, filepath)

                    if extension == 'html':
                        with open(filepath) as fh:
                            if NO_DATA_STRING in fh.read():
                                unlink(filepath)
                                continue

                    meta['files'].append({
                        'report': report_part,
                        'url': url,
                        'file': filename,
                        'filetype': extension,
                    })
                    break
                except URLError as e:
                    if e.code == 404 or e.code == 503:
                        pass
                    else:
                        raise
                finally:
                    sleep(3)

        with open(meta_file, 'w') as meta_fh:
            json.dump(meta, meta_fh, sort_keys=True, indent=2)
