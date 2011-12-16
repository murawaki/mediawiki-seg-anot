#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt
import re
from parse_mediawiki import MediaWikiWikiSegmenter
from build_article_cdb import ArticleDumpParser
from mwlib.cdbwiki import WikiDB
from mwlib.uparser import parseString
from mwlib import nuwiki
import mwlib.parser.nodes

class ArticleFilter(ArticleDumpParser):
    def __init__(self):
        self.keepRedirect = True
        self.doFiltering = False

class MediaWikiLinkExtractor(object):
    def extract(self, node, l):
        if isinstance(node, mwlib.parser.nodes.Link):
            if isinstance(node, mwlib.parser.nodes.ArticleLink):
                target = node.full_target
                if target in l:
                    l[target] += 1
                else:
                    l[target] = 1
        for c in node.children:
            self.extract(c, l)
        return l

    def stripFragment(self, l):
        p = l.find('#')
        if p >= 0:
            return l[:p]
        else:
            return l

def main(titleStream, contentdbPath, start=-1, end=1e100):
    extractor = MediaWikiLinkExtractor()
    afilter = ArticleFilter()
    contentdb = nuwiki.adapt(WikiDB(contentdbPath, lang="ja"))
    for i,line in enumerate(titleStream):
        if i < start or i > end:
            continue
        title = line.rstrip("\n").decode("utf-8")
        if afilter.isBadTitle(title):
            print "b\t%s" % title.encode("utf-8")
            continue

        text = contentdb.reader[title]
        redirect = contentdb.nshandler.redirect_matcher(text)
        if redirect is not None:
            fqname = contentdb.nshandler.get_fqname(redirect)
            print "r\t%s\t%s" % (title.encode("utf-8"), fqname.encode("utf-8"))
            continue

        if afilter.isBadContent(text):
            print "b\t%s" % title.encode("utf-8")
            continue

        # ignore exceptions; keep going
        try:
            tree = parseString(title=u"日本語", raw=text, wikidb=contentdb)
        except Exception:
            print >>sys.stderr, "failed to parse %s" % title.encode("utf-8")
            continue

        for l, c in extractor.extract(tree, dict()).iteritems():
            fqname = contentdb.nshandler.get_fqname(l)
            fqname2 = extractor.stripFragment(fqname)
            if len(fqname2) > 0:
                print "l\t%s\t%s\t%d" % (title.encode("utf-8"), fqname2.encode("utf-8"), c)

def show_usage():
    print >>sys.stderr, "python extract_links.py --input=article_titles --db=alldb"

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:e:i:d:", ["start=", "end=", "input=", "db="])
    except getopt.GetoptError, err:
        show_usage()
        exit(1)

    f = sys.stdin
    start = -1
    end = 1e100
    for o, a in opts:
        if o in ('-i', '--input'):
            f = open(a)
        elif o in ('-d', '--db'):
            contentdbPath = a
        elif o in ('-s', '--start'):
            start = int(a)
        elif o in ('-e', '--end'):
            end = int(a)

    if contentdbPath is None:
        show_usage()
        exit(1)
    main(f, contentdbPath, start=start, end=end)
    if not f == sys.stdin:
        f.close()
