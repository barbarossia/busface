'''
entry point for command line
'''

import click
import sys
from aspider import aspider
from busface.util import logger, APP_CONFIG


@click.command()
@click.option("--count", help="打印次数", type=int)
def download(count):
    """
    下载更新数据
    """
    print('start download')
    sys.argv = sys.argv[:1]
    if count is not None:
        APP_CONFIG['download.count'] = count
    sys.argv.append(APP_CONFIG['download.root_path'])
    aspider.main()


@click.group()
def main():
    pass


main.add_command(download)

if __name__ == "__main__":
    main()
