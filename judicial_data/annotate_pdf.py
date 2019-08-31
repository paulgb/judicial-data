from os import makedirs, path
from typing import List

import pdfrw
from pdf_annotate import Appearance, Location, PdfAnnotator

from judicial_data import parse_pdf

RED = (1, 0, 0)
BLUE = (0, 0, 1)


class Annotator:
    def __init__(self, filename: str):
        self.filename = filename
        self.annotations = list()
        self.get_page_dimensions()

    def get_page_dimensions(self):
        pdf = pdfrw.PdfFileReader(self.filename)
        self.num_pages = len(pdf.pages)
        self.page_width = float(pdf.pages[0].MediaBox[2])
        self.page_height = float(pdf.pages[0].MediaBox[3])

    def annotate_cols(self, cols: List[float]):
        for page in range(self.num_pages):
            for col in cols:
                loc = Location(points=[[col, 0],
                                       [col, self.page_height]], page=page)
                appearance = Appearance(stroke_color=RED,
                                        stroke_width=2)
                self.annotations.append(('line', loc, appearance))

    def annotate_text(self, text: 'parse_pdf.Text', note=None):
        loc = Location(
            x1=text.x_min, y1=self.page_height-text.y_max,
            x2=text.x_max, y2=self.page_height-text.y_min, page=text.page)
        appearance = Appearance(stroke_color=BLUE, stroke_width=1)
        self.annotations.append(('square', loc, appearance))

    def produce_debug_pdf(self):
        debug_path = path.join('debug', self.filename.split('/', 1)[1])
        makedirs(path.dirname(debug_path), exist_ok=True)

        annotator = PdfAnnotator(self.filename)
        for shape, loc, appearance in self.annotations:
            annotator.add_annotation(shape, loc, appearance)

        annotator.write(debug_path)

    def __del__(self):
        if self.annotations:
            self.produce_debug_pdf()
