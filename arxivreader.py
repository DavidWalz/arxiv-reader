"""Collect entries from arXiv: title, authors, summary ...
"""
import numpy as np
import urllib.request
import xml.dom.minidom
import time


def getNodeValue(node, tag):
    try:
        return node.getElementsByTagName(tag)[0].firstChild.nodeValue
    except IndexError:
        return ''


# search parameters
nb_queries = 100
batch_size = 10000  # maximum allowed number of results
query = 'http://export.arxiv.org/api/query?'
query += 'search_query=all'  # all:astrophysics
query += '&start=%i'
query += '&max_results=%i' % batch_size


for i in range(nb_queries):
    print(i)
    url = urllib.request.urlopen(query % (i * batch_size))
    dom = xml.dom.minidom.parseString(url.read())

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

    np.savez('batch_%i.npz' % i,
             ids=ids,
             times=times,
             titles=titles,
             summaries=summaries,
             authors=authors,
             comments=comments,
             categories=categories)
