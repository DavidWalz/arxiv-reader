"""Collect entries from arXiv: title, abstract, authors ...
"""
from __future__ import print_function
from six.moves.urllib.request import urlopen
import xml.dom.minidom
import time
import numpy


max_summary = 2000  # maximum length of summary string
max_authors = 500  # maximum length of authors string


def data_dict():
    keys = ['id', 'title', 'summary', 'time', 'comment', 'category', 'authors']
    return {k: [] for k in keys}


def retrieve(query, query_size=1000):
    dom = xml.dom.minidom.parseString(urlopen(query).read())
    entries = dom.getElementsByTagName('entry')
    if len(entries) == query_size:
        return entries
    else:
        print('  incomplete', len(entries))
        print('  retry', query)
        time.sleep(5)
        return retrieve(query, query_size)


def parse_value(node, tag):
    try:
        return node.getElementsByTagName(tag)[0].firstChild.nodeValue
    except IndexError:
        return ''


def parse_entries(entries, data):
    for entry in entries:
        # arXiv ID
        x = parse_value(entry, 'id').strip('http://arxiv.org/abs/')
        data['id'].append(x)
        # title
        x = parse_value(entry, 'title').replace('\n ', '')
        data['title'].append(x)
        # abstract
        x = parse_value(entry, 'summary').strip().replace('\n', ' ')
        x = (x[:max_summary] + '..') if len(x) > (max_summary + 2) else x
        data['summary'].append(x)
        # submission date
        x = parse_value(entry, 'published')
        data['time'].append(x)
        # comment
        x = parse_value(entry, 'arxiv:comment').replace('\n ', '')
        data['comment'].append(x)
        # category
        x = entry.getElementsByTagName('category')[0].getAttribute('term')
        data['category'].append(x)
        # authors
        x = ', '.join([n.firstChild.nodeValue for n in entry.getElementsByTagName('name')])
        x = (x[:max_authors] + '..') if len(x) > (max_authors + 2) else x
        data['authors'].append(x)
    return data


if __name__ == '__main__':
    # search parameters
    nb_files = 10  # number of batches to create
    nb_queries = 100  # number of queries per file
    query_size = 1000  # number of entries per query, max = 10000
    query_type = 'all'  # all:astrophysics, etc
    save_path = 'batch_%i.npz'

    # query, see https://arxiv.org/help/api/index
    query = 'http://export.arxiv.org/api/query?'
    query += 'search_query=%s' % query_type
    query += '&start=%i'
    query += '&max_results=%i' % query_size

    data = data_dict()

    for i in range(nb_files):
        print('file', i)

        # collect a number of queries
        for j in range(nb_queries):
            print('  query', j)
            start = (i * nb_queries + j) * query_size  # start index for query
            entries = retrieve(query % start, query_size)
            parse_entries(entries, data)
            time.sleep(3)  # play nice with the arXiv API

        # save batch
        print('saving')
        numpy.savez_compressed(save_path % i,
                id=data['id'],
                time=data['time'],
                title=data['title'],
                authors=data['authors'],
                summary=data['summary'],
                comment=data['comment'],
                category=data['category'])

        data = data_dict()
