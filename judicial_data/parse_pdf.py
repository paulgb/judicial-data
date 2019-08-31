import re
import subprocess
import tempfile
from collections import namedtuple
from datetime import date, datetime
from os import path
from typing import Iterator, List, Tuple, Optional, Dict
from xml.etree import ElementTree
import pandas as pd
from more_itertools import peekable

from judicial_data import annotate_pdf

FORMATS = ['%b %d, %Y', '%B %d, %Y']
PAGE_ELEM = r'.//{http://www.w3.org/1999/xhtml}page'
BLOCK_ELEM = r'.//{http://www.w3.org/1999/xhtml}block'
ALL_CHILDREN = './/'

Text = namedtuple('Text', ['page', 'x_min', 'x_max', 'y_min', 'y_max', 'text'])


class PDFParser:
    texts: List[Text]
    col_map: Optional[Dict[str, float]] = None

    def __init__(self, filename: str):
        self.annotator = annotate_pdf.Annotator(filename)
        self.filename = filename
        doc = self.read_pdf_as_html(filename)
        self.extract_text_parts(doc)
        self.parse_doc()

    @property
    def parts(self) -> Iterator[List[Text]]:
        text_iter = peekable(self.texts)
        page = 0
        while text_iter:
            text = next(text_iter)
            line: List[Text] = [text]
            y = text.y_max
            page = text.page

            while text_iter and text_iter.peek().page == page and text_iter.peek().y_min < y:
                line.append(next(text_iter))
            yield sorted(line, key=lambda x: x.x_min)

    @staticmethod
    def parse_date(d: str) -> Optional[date]:
        for fmt in FORMATS:
            try:
                return datetime.strptime(d, fmt).date()
            except ValueError:
                pass
        return None

    @staticmethod
    def read_pdf_as_html(pdf_file):
        with tempfile.TemporaryDirectory() as temp_dir:
            #result_file = path.join(temp_dir, 'result.html')
            result_file = 'temp.html'

            subprocess.check_call([
                'pdftotext',
                pdf_file,
                result_file,
                '-htmlmeta',
                '-bbox-layout',
            ])

            return ElementTree.parse(result_file)

    def extract_text_parts(self, doc):
        root = doc.getroot()
        pages = root.findall(PAGE_ELEM)

        self.page_width = float(pages[0].attrib['width'])
        self.page_height = float(pages[0].attrib['height'])
        self.num_pages = len(pages)

        texts = []

        for i, page in enumerate(pages):
            lines = page.findall(BLOCK_ELEM)
            for line in lines:
                t = ' '.join(a.text
                             for a in line.findall(ALL_CHILDREN)).strip()
                attr = line.attrib
                texts.append(Text(i,
                                  float(attr['xMin']),
                                  float(attr['xMax']),
                                  float(attr['yMin']),
                                  float(attr['yMax']), t))

        self.texts = list(
            sorted(texts, key=(lambda x: (x.page, x.y_min, x.x_min))))

    def get_column_from_x(self, x):
        return next(c for c, x_ in reversed(list(self.col_map.items())) if x_ <= x)

    def parse_doc(self):
        self.rows = []
        stop_collecting = False
        for group in self.parts:
            alltext = ' '.join(a.text for a in group)

            if alltext.startswith('Vacancies in the Federal Judiciary'):
                self.annotator.annotate_group(group, annotate_pdf.GREY)
            elif alltext.startswith('Total Vacancies:'):
                self.annotator.annotate_group(group, annotate_pdf.GREEN)
                if 'Total Nominees Pending' in alltext:
                    total_vac = int(alltext.split()[-2])
                    total_noms = total_vac = int(alltext.split()[-1])
                else:
                    total_vac = int(alltext.split(' ')[-1])
            elif alltext.startswith('Total Nominees Pending:'):
                self.annotator.annotate_group(group, annotate_pdf.GREEN)
                total_noms = int(alltext.split(' ')[-1])
            elif group[0].text in ['Circuit', 'Court']:
                self.create_col_map(group)
            elif self.parse_date(alltext):
                self.annotator.annotate_group(group, annotate_pdf.GREEN)
                date = self.parse_date(alltext)
            elif group[0].text.endswith(' Circuit') or alltext == 'International Trade':
                self.annotator.annotate_group(group, annotate_pdf.GREEN)
                circuit = group[0].text
                court = None
            elif alltext == 'VACANCIES':
                stop_collecting = True # Hit end of document, don’t treat as table
            elif alltext.startswith('Federal Judicial Vacancies') or alltext.startswith('http:'):
                self.annotator.annotate_group(group, annotate_pdf.GREY)
            elif not stop_collecting:
                if not self.col_map:
                    print('no col mappings')
                    continue
                r = {
                    self.get_column_from_x(t.x_min): t.text
                    for t in group
                }

                for c in ['Vacancy Date', 'Nomination']:
                    if c in r:
                        r[c] = pd.Timestamp(r[c]).date()

                if len(r) == 1 and 'Court' in r:
                    court = r['Court']
                    self.annotator.annotate_group(group, annotate_pdf.PURPLE)
                    continue

                if 'Nominee' not in r:
                    r['Nominee'] = None
                if 'Nomination' not in r:
                    r['Nomination'] = None

                if 'Circuit' not in r:
                    r['Circuit'] = court
                else:
                    court = r['Circuit']
                r['CT'] = circuit
                
                r['date'] = date
                self.annotator.annotate_group(group, annotate_pdf.BLUE)
                self.rows.append(r)

    def create_col_map(self, group):
        col_mappings = {}
        last_max = None

        for t in group:
            self.annotator.annotate_text(t)

            name = t.text
            name = re.sub(r'\s+', ' ', name)
            if last_max is None:
                loc = t.x_min
            else:
                loc = (last_max + t.x_min) / 2
            last_max = t.x_max
            col_mappings[name] = loc - 10

        self.annotator.annotate_cols(col_mappings.values(), group[0].page)
        self.col_map = col_mappings
