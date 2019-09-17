from argparse import ArgumentParser
from glob import glob
from os.path import splitext
from typing import List

from judicial_data.parse_html import parse_html
from judicial_data.parse_pdf import PDFParser

def convert_all(files: List[str] = None):
    if not files:
        files = sorted(glob('raw/*/vacancies.*', recursive=True))

    for filename in files:
        _, base, fn = filename.split('/')
        _, ext = splitext(fn)

        try:
            if ext == '.html':
                print(filename)
                result = parse_html(filename)
            elif ext == '.pdf':
                print(filename)
                result = PDFParser(filename).parse_doc()
            else:
                raise ValueError()

            if result is not None:
                result.to_csv(f'data/{base}.csv', index=False)
        except ValueError:
            #print(f'error')
            raise


def main():
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', default=None)
    args = parser.parse_args()
    convert_all(args.files)


if __name__ == '__main__':
    main()
