from glob import glob
from os.path import splitext, basename

from judicial_data.parse_html import parse_html


def convert_all():
    for filename in sorted(glob('raw/*')):
        base, ext = splitext(basename(filename))
        try:
            if ext == '.html':
                print(filename)
                result = parse_html(filename)
            else:
                raise ValueError()
            
            result.to_csv(f'data/{base}.csv', index=False)
        except ValueError:
            print(f'error')


if __name__ == '__main__':
    convert_all()
