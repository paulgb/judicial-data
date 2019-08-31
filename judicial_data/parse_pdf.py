import re
import subprocess
import tempfile
from collections import namedtuple
from datetime import datetime
from os import path
from typing import List
from xml.etree import ElementTree
from judicial_data import annotate_pdf
from more_itertools import peekable


FORMATS = ['%b %d, %Y', '%B %d, %Y']
PAGE_ELEM = r'.//{http://www.w3.org/1999/xhtml}page'
BLOCK_ELEM = r'.//{http://www.w3.org/1999/xhtml}block'
ALL_CHILDREN = './/'

Text = namedtuple('Text', ['page', 'x_min', 'x_max', 'y_min', 'y_max', 'text'])


class PDFParser:
    def __init__(self, filename: str):
        self.annotator = annotate_pdf.Annotator(filename)

        self.filename = filename
        doc = self.read_pdf_as_html(filename)
        self.extract_text_parts(doc)
        self.col_map = self.create_col_map()

    @property
    def parts(self):
        text_iter = peekable(iter(self.texts))
        while text_iter:
            text = next(text_iter)
            line = [text]
            y = text.y_max

            while text_iter.peek().y_min < y:
                line.append(next(text_iter))
            yield line

    @staticmethod
    def parse_date(d: str) -> datetime:
        for fmt in FORMATS:
            try:
                return datetime.strptime(d, fmt).date()
            except ValueError:
                pass
        return None

    @staticmethod
    def read_pdf_as_html(pdf_file):
        with tempfile.TemporaryDirectory() as temp_dir:
            result_file = path.join(temp_dir, 'result.html')

            subprocess.check_call([
                'pdftotext',
                pdf_file,
                result_file,
                '-htmlmeta',
                '-bbox-layout',
            ])

            return ElementTree.parse(result_file)

    def extract_text_parts(self, doc) -> List[Text]:
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

    def create_col_map(self):
        col_mappings = {}
        for group in self.parts:
            print(group)
            if group[0].text in {'Circuit', 'Court'}:
                for t in group:
                    self.annotator.annotate_text(t)

                    name = t.text
                    name = re.sub(r'\s+', ' ', name)
                    loc = t.x_min - 10
                    col_mappings[name] = loc

                self.annotator.annotate_cols(col_mappings.values())
                return col_mappings
