'''
entry point for command line
'''

import click
import sys
from aspider import aspider
from busface.util import logger, APP_CONFIG
import busface.model.classifier as clf
import busface.upload as up

@click.command()
@click.option("--file", help="file name", type=str)
@click.option("--rate", help="rate", default=1, type=int)
def upload(file, rate):
    '''
    根据现有模型预测推荐数据
    '''
    try:
        up.upload(file, rate)
    except FileNotFoundError:
        click.echo('file not found')


@click.command()
def recommend():
    '''
    根据现有模型预测推荐数据
    '''
    try:
        clf.recommend()
    except FileNotFoundError:
        click.echo('还没有训练好的模型, 无法推荐')

@click.command()
def train():
    '''
    根据现有模型预测推荐数据
    '''
    try:
        clf.train()
    except ValueError:
        click.echo('训练数据不足, 无法训练模型')


@click.command()
@click.option("--count", help="打印次数", type=int)
def download(count):
    """
    下载更新数据
    """
    print('start download')

    sys.argv = sys.argv[:1]
    if count is None:
        download_count = APP_CONFIG['download.count']
    else:
        download_count = count
    roots = []
    roots.append(APP_CONFIG['download.root_path'])
    options = {'roots': roots, 'no_parse_links': False, 'count': download_count}
    print(options)
    aspider.download(extra_args=options)


@click.group()
def main():
    pass


main.add_command(upload)
main.add_command(download)
main.add_command(recommend)
main.add_command(train)

if __name__ == "__main__":
    main()
