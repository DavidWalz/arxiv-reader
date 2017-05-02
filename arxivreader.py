"""Collect entries from arXiv: title, abstract, authors ...

Example queries, see https://arxiv.org/help/api/index
    all:electron
    cat:astro-ph
    cat:astro-ph.HE

Entries as of may 2017
(0 entries means that sub-categories have to be queried instead, eg. "cs.CV")
    astro-ph 105380
    cond-mat 14215
    hep-ex 33529
    hep-lat 20428
    hep-ph 129308
    hep-th 116546
    math-ph 49450
    quant-ph 79667
    nucl-ex 16329
    nucl-th 39794
    physics 0
    qr-qc 0
    nlin 0
    math 0
    cs 0
    q-bio 1356
    q-fin 0
    stat 0
"""
from __future__ import print_function
from six.moves.urllib.request import urlopen
import feedparser
import time
import numpy


BASE_URL = 'http://export.arxiv.org/api/query?search_query='


def retrieve_number_of_entries(query):
    url = BASE_URL + query + '&max_results=1'
    feed = feedparser.parse(urlopen(url).read())
    return int(feed.feed.opensearch_totalresults)


def retrieve(query, max_results=1000, start=0, nb_retry=10):
    """ Query arXiv entries and retry if incomplete """
    url = BASE_URL + query + '&start=%i&max_results=%i' % (start, max_results)
    for i in range(nb_retry):
        feed = feedparser.parse(urlopen(url).read())
        nb_results = len(feed.entries)
        if nb_results == max_results:
            return feed
        print('Incomplete %i/%i, retrying in 5s' % (nb_results, max_results))
        time.sleep(5)


def shorten(x, length):
    """ Shorten string x to length, adding '..' if shortened """
    if len(x) > (length):
        return x[:length - 2] + '..'
    return x


def parse_entries(entries, data, max_authors=500, max_summary=2000):
    for entry in entries:
        # arXiv ID
        data['id'].append(entry['id'].strip('http://arxiv.org/abs/'))
        # title
        data['title'].append(entry['title'].replace('\n ', ''))
        # publication date
        data['time'].append(entry['published'])
        # category
        data['category'].append(entry['category'])
        # authors
        x = ', '.join([a['name'] for a in entry['authors']])
        x = shorten(x, max_authors)
        data['authors'].append(x)
        # abstract
        x = entry['summary'].strip().replace('\n', ' ')
        x = shorten(x, max_summary)
        data['summary'].append(x)
    return data


if __name__ == '__main__':
    # search parameters
    query = 'cat:astro-ph'  # all:astrophysics, etc
    save_path = 'astroph_batch_%i.npz'

    ntot = retrieve_number_of_entries(query)
    print('Query: %s, Entries: %i' % (query, ntot))

    file_size = 10000  # number of entries per file
    query_size = 1000  # number of entries per query, max = 10000

    nb_files = ntot // file_size
    nb_queries = file_size // query_size

    for i in range(nb_files):
        print('file', i)
        data = {k: [] for k in ['id', 'title', 'summary', 'time', 'category', 'authors']}

        # collect a number of queries
        for j in range(nb_queries):
            print('  query', j)
            start = (i * nb_queries + j) * query_size
            feed = retrieve(query, query_size, start)
            data = parse_entries(feed.entries, data)
            time.sleep(3)

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
