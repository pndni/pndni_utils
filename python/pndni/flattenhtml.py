from html.parser import HTMLParser
import sys
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


def main():
    htmldir = Path(sys.argv[1]).parent
    parser = FlattenImages(htmldir)
    with open(sys.argv[1], 'r') as f:
        for l in f:
            parser.feed(l)


if __name__ == '__main__':
    main()
