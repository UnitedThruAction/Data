"""A simple, generic table parser for HTML.

Inputs:
- source: URL or (plain) filename
- addl_data: dict of additional data to add to each row

Outputs:
- List of dicts containing data from largest table on page

@author n.o.franklin@gmail.com
@date 2017-12-30
"""

from requests import get
from bs4 import BeautifulSoup

def generic_table_parser(source, addl_data):
    if source[:4] == 'http':
        response = get(source)
        response.raise_for_status()
        fh = response.text
    else:
        fh = open(source, 'r')

    soup = BeautifulSoup(fh, 'lxml')
    tabs = soup.find_all('table')

    # Find largest table
    tab_sizes = {}
    for i, tab in enumerate(tabs):
        rows = tab.find_all('tr')
        row_num = 0
        for row in rows:
            row_num += 1
        tab_sizes[row_num] = i
    largest_index = tab_sizes[sorted(tab_sizes.keys(), reverse=True)[0]]

    # Get table headings
    headings = []
    for header in tabs[largest_index].find_all('th'):
        headings.append(header.text)
    if not headings:
        raise Exception("No table headings found.")

    # Get table data
    results = []
    for row in tabs[largest_index].find_all('tr'):
        cells = row.find_all('td')
        if len(cells) == len(headings):
            row_data = {headings[i]: cell.text for i, cell in enumerate(cells)}
            row_data.update({'source': source})
            row_data.update(addl_data)
            results.append(row_data)

    return results
