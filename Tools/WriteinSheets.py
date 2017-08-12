"""Generates HTML-format write-in sheets for volunteers to record voter contact.
Easy to print in modern browsers: HTML tables automatically wrap to pages.

@author n.o.franklin@gmail.com
"""

from yattag import Doc


def generate_html(filename, dataframe):
    """Print HTML format write-in sheet for voter contact.

    Arguments:
        filename (str)
        dataframe (pandas.DataFrame): in NY State Voter File format

    """

    doc, tag, text = Doc().tagtext()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('head'):
            with tag('style'):
                text(
                    'table, th, td {border: 1px solid black; border-collapse: collapse; table-layout: fixed; font-family: Arial, Helvetica, sans-serif; font-size:10px;} ')
                text(
                    'h1, h2, h3, p {font-family: Arial, Helvetica, sans-serif;}} ')
                text('th, td {padding: 2px;} ')
                text('p.thick {font-weight: bold;} ')
                text('@media print {div {page-break-inside: avoid;}}')
        with tag('body'):
            with tag('h1'):
                text(filename)
            for row in dataframe.iterrows():
                voter = row[1]
                with tag('p'):
                    with tag('div'):
                        with tag('table', width='100%'):
                            with tag('tr'):
                                with tag('td'):
                                    text(voter['COUNTYVRNUMBER'])
                                with tag('td'):
                                    text(voter['FIRSTNAME'])
                                with tag('td'):
                                    text(voter['LASTNAME'])
                                with tag('td'):
                                    text(voter['STREET ADDRESS'])
                                with tag('td'):
                                    text(voter['RAPARTMENT'])
                                with tag('td'):
                                    text(voter['PARTY NAME'])
                            with tag('tr'):
                                with tag('td', colspan=3):
                                    text('Email address')
                                with tag('td', colspan=3):
                                    text('Phone Number')
                            with tag('tr', rowspan=8, valign='TOP'):
                                with tag('td', colspan=2, align='center'):
                                    with tag('p', klass='thick'):
                                        text('Interaction')
                                    with tag('table'):
                                        for name in [
                                            'Discussed',
                                            'Registered to Vote',
                                            'Registered to change affiliation',
                                            'Refused',
                                            'Other Language',
                                            'Not Home',
                                            'Moved',
                                                'Dead']:
                                            with tag('tr'):
                                                with tag('td'):
                                                    # check-box
                                                    doc.asis('&#9634;')
                                                with tag('td'):
                                                    text(name)
                                with tag('td', colspan=1, align='center'):
                                    with tag('p', klass='thick'):
                                        text('Contact Choice')
                                    with tag('table'):
                                        for choice in [
                                                'Only call regarding a reminder to vote', 'No fundraising']:
                                            with tag('tr'):
                                                with tag('td'):
                                                    # check-box
                                                    doc.asis('&#9634;')
                                                with tag('td'):
                                                    text(choice)
                                with tag('td', align='center'):
                                    with tag('p', klass='thick'):
                                        text('Category')
                                    with tag('table'):
                                        for choice in [
                                                'Committed', 'Unaware', 'Transactional']:
                                            with tag('tr'):
                                                with tag('td'):
                                                    # check-box
                                                    doc.asis('&#9634;')
                                                with tag('td'):
                                                    text(choice)
                                with tag('td', colspan=2, align='center'):
                                    with tag('p', klass='thick'):
                                        text('Issues')
                            with tag('tr'):
                                for i in [
                                        'Rating: 1', '2', '3', '4', '5', 'Not Sure']:
                                    with tag('td'):
                                        text(i)

                doc.stag('br')
                doc.stag('br')

    with open(filename) as outhandle:
        outhandle.write(doc.getvalue())
