#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt
from parse_mediawiki import MediaWikiWikiSegmenter
from mwlib.cdbwiki import WikiDB
from mwlib.uparser import parseString
from mwlib import nuwiki


def main(titleStream, contentdbPath, start=-1, end=1e100, doSegment=True, lang="ja"):
    segmenter = MediaWikiWikiSegmenter()
    # templdb = nuwiki.adapt(WikiDB(templdbPath, lang="ja"))
    # contentdb = WikiDB(contentdbPath, lang="ja")
    contentdb = nuwiki.adapt(WikiDB(contentdbPath, lang=lang))
    for i,line in enumerate(titleStream):
        if i < start or i > end:
            continue
        title = line.rstrip("\n").decode("utf-8")
        text = contentdb.reader[title]

        if text.find("#REDIRECT", 0, 256) >= 0:
            continue

        # ignore exceptions; keep going
        try:
            # tree = parseString(title=u"日本語", raw=text, wikidb=templdb)
            tree = parseString(title=title, raw=text, wikidb=contentdb)
        except Exception as detail:
            print >>sys.stderr, "failed to parse %s: %s" % (title.encode("utf-8"), detail)
            continue

        output = segmenter.traverse(tree, [], 0)
        output = segmenter.cleanOutput(output)

        if len(output) > 0:
            print title.encode("utf-8")
            segmenter.printOutput(output, doSegment=doSegment)
            print "__ARTICLE__"

def show_usage():
    print >>sys.stderr, "usage: python parse_dump.py --input=titlelist --db=contentdb"

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:e:i:d:l:", ["start=", "end=", "input=", 'db=', 'plain', 'lang='])
    except getopt.GetoptError, err:
        show_usage()
        exit(0)

    f = sys.stdin
    start = -1
    end = 1e100
    doSegment = True
    lang = "ja"
    for o, a in opts:
        if o in ('-i', '--input'):
            f = open(a)
        elif o in ('-l', '--lang'):
            lang = a
        elif o in ('-d', '--db'):
            contentdbPath=a
        elif o in ('-s', '--start'):
            start = int(a)
        elif o in ('-e', '--end'):
            end = int(a)
        elif o in ('--plain'):
            doSegment = False
    if contentdbPath is None:
        show_usage()
        exit(0)

    main(f, contentdbPath, start=start, end=end, doSegment=doSegment, lang=lang)
    if not f == sys.stdin:
        f.close()
