#!/bin/env python
#-*- encoding: utf-8 -*-

import os
import os.path
import click
import json
from string import Template

from pyrrd.rrd import RRD
from pyrrd.backend import bindings

import munincustom
from munincustom.utils.config import ConfigReader
from munincustom.utils.parser import MuninConfigParser, MuninDataParser

from  munincustom.exceptions import FileNotFoundError

def valid_data(checker, *paths):
    return reduce(lambda acc,x: acc and checker(x), paths, True)

@click.group()
def cmd():
    pass

@cmd.group()
def make():
    pass

@cmd.group()
def load():
    pass

@make.command()
@click.option('--conf', help='mc configuration file path.')
@click.option('--mconf', help='munin configuration file path.')
@click.option('--dest', help='destination file path.')
@click.option('--tmpl', help='template file path.')
@click.option('--part', help='partial template file path.')
@click.option('--folder', help='folder name for munin custom url.')
@click.option('--name', help='name for custom munin page')
def template(conf, mconf, dest, tmpl, folder, part, name):

    chk_path = lambda path: bool(isinstance(path, str) and os.path.isfile(path))
    chk_not_none = lambda x: x is not None

    config = ConfigReader(conf)

    if mconf is None:
        mconf = config.get('mc', 'munin_conf')

    if tmpl is None:
        tmpl = config.get('template_opt', 'template_file')

    if folder is None:
        folder = config.get('template_opt', 'folder_name')

    if part is None:
        part = config.get('template_opt', 'partial_file')

    if name is None:
        name = config.get('template_opt', 'page_name')

    if not valid_data(chk_path, mconf, tmpl, part):
        raise FileNotFoundError(';'.join([str(mconf), str(tmpl), str(part)]))

    _, munin_options = MuninConfigParser(mconf).parse()
    default_dest_path = munin_options['tmpldir'] if 'tmpldir' in munin_options else None
    if dest is None:
        dest = config.get('template_opt', 'dest_file', default_dest_path)

    if not valid_data(chk_not_none, folder, name, dest):
        raise ValueError('Data is None')

    partial = Template(open(part).read()).substitute(
                customview_folder=folder,
                customview_name=name
            )
    template_body = Template(open(tmpl).read()).substitute(customview=partial)
    open(dest, 'w').write(template_body)




@make.command()
@click.option('--conf', help='mc configuration file path.')
@click.option('--mconf', help='munin configuration file path.')
@click.option('--dest', help='destination folder path.')
def content(conf, mconf, dest):
    pass



@load.command()
@click.option('--conf', help='mc configuration file path.')
@click.option('--mconf', help='munin configuration file path.')
@click.option('--dest', help='destination folder path.')
def graph(conf, mconf, dest):
    chk_path = lambda path: bool(isinstance(path, str) and os.path.isfile(path))

    config = ConfigReader(conf)

    if mconf is None:
        mconf = config.get('mc', 'munin_conf')


    if not valid_data(chk_path, mconf):
        raise FileNotFoundError(mconf)

    machines, options = MuninConfigParser(mconf, dict(config.items('munin_config'))).parse()
    datafile = options['dbdir'] + '/datafile'
    graph_info = MuninDataParser(datafile).parse()

    for mt, v in graph_info.items():
        for path, graph in v.items():
            for s in graph.series:
                filepath = options['dbdir'] + '/' + s.get_rrd_filepath()
                print('loading: ' + filepath)
                rrd = RRD(filepath, mode='r', backend=bindings)
                data = rrd.fetch(start="-30minutes")['42']
                content_dist = config.get('mc', 'content_dist', options['htmldir']) + '/'
                output_file = content_dist + s.get_result_filepath()
                print('output: ' + output_file)
                dir_name = os.path.dirname(output_file)
                if not os.path.lexists(dir_name):
                    os.makedirs(dir_name)
                fp = open(output_file, mode='w')
                json.dump(data, fp, indent=4)
                print('end')








def main():
    cmd()


if __name__ == '__main__':
    main()

