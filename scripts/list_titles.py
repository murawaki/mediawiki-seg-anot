#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NOTE: this may contain redirects and disambiguation pages
#   If you only need article titles, use list_article_titles.pl instead
#
import sys
from mwlib.cdb.cdbwiki import WikiDB
from mwlib import nuwiki
from mwlib.nshandling import nshandler

# contentdb = '/willow4/murawaki/compound/data/contentdb'

def main(contentdb):
    db = WikiDB(contentdb, lang="ja")
    contentdb = nuwiki.adapt(db)
    handler = nshandler(contentdb.siteinfo)
    for title in db.reader.iterkeys():
        if handler.splitname(title)[0] == 0: # NS_MAIN namespace
            print title.encode("utf-8")

if __name__ == "__main__":
    main(sys.argv[1])
