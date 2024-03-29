#!/bin/bash
echo "Downloading trace MSR Cambridge Traces 2" 1>&2
cookies=/tmp/cookie$$
cat > $cookies << 'EOF'
# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This file was generated by iotta.snia.org! Edit at your own risk.

server2.iotta.snia.org	FALSE	/	FALSE	0	infodigest	1ec4ce6028592d2276ede913bd6d6f25f75fb2a1
server2.iotta.snia.org	FALSE	/	FALSE	0	legal	true
server2.iotta.snia.org	FALSE	/	FALSE	0	id	387639
EOF

function useWGET {
  wget --load-cookies=$cookies \
    -O 'msr-cambridge2.tar' -c 'http://server2.iotta.snia.org/traces/387/download?type=file&sType=wget'
}
function useCURL {
  curl -b $cookies -o \
    'msr-cambridge2.tar' -C - -L 'http://server2.iotta.snia.org/traces/387/download?type=file&sType=curl'
}

if which wget >/dev/null 2>&1; then
  useWGET
elif which curl >/dev/null 2>&1; then
  useCURL
else
  echo "Couldn't find either wget or curl. Please install one of them" 1>&2
fi

rm -f $cookies
set -e
