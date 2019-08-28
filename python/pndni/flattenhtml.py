import argparse
from html.parser import HTMLParser
from pathlib import Path
import base64


class FlattenImages(HTMLParser):

    def __init__(self, htmldir):
        self.htmldir = htmldir
        super().__init__()

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            newattrs = []
            for key, val in attrs:
                if key == 'src':
                    if val[-4:] != '.png':
                        raise RuntimeError('Only png supported. {}'.format(val))
                    with open(Path(self.htmldir, val), 'rb') as f:
                        imgdata = base64.b64encode(f.read()).decode()
                    val = f'data:image/png;base64,{imgdata}'
                newattrs.append((key, val))
            print(f'<{tag} ' + ' '.join((f'{key}="{val}"' for key, val in newattrs)) + '>', end='')
        else:
            print(self.get_starttag_text(), end='')

    def handle_endtag(self, tag):
        print(f'</{tag}>', end='')

    def handle_data(self, data):
        print(data, end='')

    def handle_comment(self, data):
        print(f'<!--{data}-->', end='')

    def handle_decl(self, decl):
        print(f'<!{decl}>')

    def handle_pi(self, data):
        print(f'<?{data}>')


def get_parser():
    parser = argparse.ArgumentParser(description="""
Convert an html file with dependent png images into a flat file (i.e., embed those images into the html file). Currently only
png images are supported, and any other image format will cause an error.

.. code-block:: bash

   flattenhtml input.html > output.html

""")
    parser.add_argument('input_file', type=str, help='Input html file.')
    return parser


def main():
    args = get_parser().parse_args()
    htmldir = Path(args.input_file).parent
    htmlparser = FlattenImages(htmldir)
    with open(args.input_file, 'r') as f:
        for l in f:
            htmlparser.feed(l)


if __name__ == '__main__':
    main()
