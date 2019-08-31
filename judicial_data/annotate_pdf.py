from os import makedirs, path
from typing import List, Tuple

import pdfrw
from pdf_annotate import Appearance, Location, PdfAnnotator

from judicial_data import parse_pdf

RED = (1, 0, 0)
BLUE = (0, 0, 1)
GREY = (0.3, 0.3, 0.3)
GREEN = (0, 1, 0)
PURPLE = (1, 0, 1)

class Annotator:
    def __init__(self, filename: str):
        self.filename = filename
        self.annotations: List[Tuple[str, Location, Appearance]] = list()
        self.get_page_dimensions()

    def get_page_dimensions(self):
        pdf = pdfrw.PdfFileReader(self.filename)
        self.num_pages = len(pdf.pages)
        self.page_width = float(pdf.pages[0].MediaBox[2])
        self.page_height = float(pdf.pages[0].MediaBox[3])

    def annotate_cols(self, cols: List[float], page: int):
        for col in cols:
            loc = Location(points=[[col, 0],
                                    [col, self.page_height]], page=page)
            appearance = Appearance(stroke_color=RED,
                                    stroke_width=2)
            self.annotations.append(('line', loc, appearance))

    def annotate_text(self, text: 'parse_pdf.Text', color=BLUE):
        loc = Location(
            x1=text.x_min, y1=self.page_height-text.y_max,
            x2=text.x_max, y2=self.page_height-text.y_min, page=text.page)
        appearance = Appearance(stroke_color=color, stroke_width=1)
        self.annotations.append(('square', loc, appearance))

    def annotate_group(self, texts: List['parse_pdf.Text'], color=BLUE):
        x1 = min(t.x_min for t in texts)
        x2 = max(t.x_max for t in texts)
        y1 = min(t.y_min for t in texts)
        y2 = min(t.y_max for t in texts)
        loc = Location(
            x1=x1, y1=self.page_height-y2,
            x2=x2, y2=self.page_height-y1, page=texts[0].page)
        appearance = Appearance(stroke_color=color, stroke_width=1)
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
