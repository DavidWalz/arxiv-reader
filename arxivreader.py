"""Collect entries from arXiv: title, authors, summary ...
"""
from six.moves.urllib.request import urlopen
import xml.dom.minidom
import time
import numpy as np


def getNodeValue(node, tag):
    try:
        return node.getElementsByTagName(tag)[0].firstChild.nodeValue
    except IndexError:
        return ''


# search parameters
nb_queries = 200
batch_size = 5000  # number of results per query, max = 10000
query = 'http://export.arxiv.org/api/query?'
query += 'search_query=all'  # all:astrophysics
query += '&start=%i'
query += '&max_results=%i' % batch_size
save_path = 'batch_%i.npz'

for i in range(nb_queries):
    print(i)

    dom = xml.dom.minidom.parseString(urlopen(query % (i * batch_size)).read())

    ids = []
    times = []
    titles = []
    summaries = []
    authors = []
    comments = []
    categories = []

    # parse query results
    for entry in dom.getElementsByTagName('entry'):
        ids.append(getNodeValue(entry, 'id'))

        title = getNodeValue(entry, 'title').replace('\n ', '')
        titles.append(title)

        summary = getNodeValue(entry, 'summary').strip()
        summaries.append(summary)

        times.append(getNodeValue(entry, 'published'))

        comment = getNodeValue(entry, 'arxiv:comment').replace('\n ', '')
        comments.append(comment)

        category = entry.getElementsByTagName('category')[0].getAttribute('term')
        categories.append(category)

        names = entry.getElementsByTagName('name')
        authors.append(', '.join([n.firstChild.nodeValue for n in names]))

    time.sleep(3)  # play nice with the arXiv API

    np.savez(save_path % i,
             ids=ids,
             times=times,
             titles=titles,
             summaries=summaries,
             authors=authors,
             comments=comments,
             categories=categories)
