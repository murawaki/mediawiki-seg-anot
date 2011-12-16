#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt
import re, unicodedata
from mwlib.cdbwiki import BuildWiki
from mwlib.dumpparser import DumpParser

wikiLang = 'bn'

class ArticleDumpParser(DumpParser):
    badNS = re.compile(u"^(?:利用者|ノート|Wikipedia|画像|Help|Portal|Template|ファイル|Category|MediaWiki|W)(?:\:|‐)")
    aimaiRE = re.compile(u"\{\{([Aa]imai|[Dd]isambig|曖昧さ回避|人名の曖昧さ回避|地名の曖昧さ回避|山の曖昧さ回避)")
    if wikiLang == 'bn':
        badNS = re.compile(u"^(?:মিডিয়া|বিশেষ|আলাপ|ব্যবহারকারী|চিত্র|মিডিয়াউইকি|টেমপ্লেট|সাহায্য|বিষয়শ্রেণী|উইকিপিডিয়া)(?:\:|‐)")

    def __init__(self, dumpPath, keepRedirect=False, doFiltering=False):
        super(ArticleDumpParser, self).__init__(dumpPath)
        self.keepRedirect = keepRedirect
        self.doFiltering = doFiltering

    def handlePageElement(self, pageElem):
        res = super(ArticleDumpParser, self).handlePageElement(pageElem)
        if res is None:
            return None
        if res.redirect and not self.keepRedirect:
            return None
        if ArticleDumpParser.badNS.search(res.title) is not None:
            return None
        if self.doFiltering:
            if self.isBadTitle(res.title):
                return None
            if self.isBadContent(res.text):
                return None
        return res

    # copy from extract_text_from_wikipedia.pl
    def isBadTitle(self, utitle):
        if re.search("^\d+$", utitle) or \
                re.search(u"^\d+(?:年|年代|世紀|月)$", utitle) or \
                re.search(u"^\d+月\d+日$", utitle):
            return True
        if len(utitle) == 1 and \
                re.match(unicodedata.name(utitle[0]), "(HIRAGANA|KATAKANA)"):
            # one-character hiragana/katakana
            return True
        # must contain at least one 'Letter'
        hasLetter = False
        for uchar in utitle:
            if unicodedata.category(uchar)[0] == 'L': # Letter
                hasLetter = True
                break
        if hasLetter is False:
            return True
        # disambiguation page
 	if re.search(u"一覧$", utitle):
            return True
        # disambiguation page
 	if re.search(u"\(曖昧さ回避\)", utitle):
            return True
        return False

    def isBadContent(self, utext):
        if ArticleDumpParser.aimaiRE.search(utext) is not None:
            return True
        return False

def main(dumpPath, dbDir, keepRedirect=False, doFiltering=False):
    print >>sys.stderr, "keepRedirect: %s\tdoFiltering: %s" % (keepRedirect, doFiltering)
    p = ArticleDumpParser(dumpPath, keepRedirect=keepRedirect, doFiltering=doFiltering)
    BuildWiki(p, outputdir=dbDir)()
    
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "rf", ["keep-redirect", "filter"])
    except:
        print >>sys.stderr, "usage: %s [options] dumpPath dbDir" % sys.argv[0]
        exit(0)

    keepRedirect = False
    doFiltering = False
    for o, a in opts:
        if o in ('-r', '--keep-redirect'):
            keepRedirect = True
        elif o in ('-f', '--filter'):
            doFiltering = True

    main(args[0], args[1], keepRedirect=keepRedirect, doFiltering=doFiltering)
