#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from mwlib.cdbwiki import BuildWiki
from mwlib.dumpparser import DumpParser

class TemplateOnlyDumpParser(DumpParser):
    def handlePageElement(self, pageElem):
        res = super(TemplateOnlyDumpParser, self).handlePageElement(pageElem)
        if res is not None and res.title.find("Template:", 0) == 0:
            print >>sys.stderr, "register %s" % res.title
            return res
        else:
            return None

def main(dumpPath, dbDir):
    p = TemplateOnlyDumpParser(dumpPath)
    BuildWiki(p, outputdir=dbDir)()
    
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
