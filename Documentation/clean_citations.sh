#!/bin/bash

#
#
# YOU WILL NEED GNU SED FOR THIS TO WORK - MacOSX SED DOESN'T WORK!!!
# On Mac do a brew install sed and add it to the path and make sure
# it uses gnu sed.

# in principle applying this a second time is without any effect
 
BIBPATH=./
 
for file in $BIBPATH/*.bib; do
    # delete abstract, file, urldate entries
    sed -i -r '/(abstract|file|note|urldate|address|isbn|issn) =/d' $file
 
    # surround titles with brackets to protect from lowercase, but first remove added brackets
    sed -i -r '/title/s/\{([a-zA-Z]+)\}^,/\1/' $file
    sed -i -r 's/title = (\{.+\})/title = {\1}/' $file
 
    # for arxiv entries, replace url and journal by preprint fields
    sed -i -r 's/url = \{http:\/\/arxiv.org\/abs\/([a-z0-9/-]+)\}/archivePrefix = "arXiv",\n\teprint = "\1"/' $file
    sed -i -r 's/url = \{http:\/\/arxiv.org\/abs\/([0-9.]+)\}/archivePrefix = "arXiv",\n\teprint = "\1"/' $file
    sed -i -r '/journal = \{+arXiv/d' $file
 
    # replace the protected dollar
    sed -i -r 's/\\\$/$/g' $file
    # fix latex formula (only in title)
    sed -i -r '/title/s/\{\\textbackslash\}/\\/g' $file
    sed -i -r '/title/s/\\\{/\{/g' $file
    sed -i -r '/title/s/\\\}/\}/g' $file
    # note that we can not define set in titles
 
    # delete url if doi is present (works only if it is the line just before)
    # http://www.theunixschool.com/2012/06/sed-25-examples-to-delete-line-or.html
    sed -i -n '/doi =/{x;/url =/d;x;};1h;1!{x;p;};${x;p}' $file
 
    # delete empty url field (e.g. because of arxiv deletion)
    sed -i -r '/url = \{\},/d' $file
    # delete all brackets when there are more than 2
    sed -i -r 's/\{{3,}(.+)\}{3,}/{{\1}}/' $file
 
    # remove leading blank lines
    sed -i -r '/./,$!d' $file
done
