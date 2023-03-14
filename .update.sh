#!/bin/sh

PROJECT=slackfix
SRCDIST=~/src/git/$PROJECT/dist
SPEC=$PROJECT.spec
VERSION=$(sed -n 's/^Version:[ \t]*\([0-9\.]*\).*$/\1/p' $SPEC)
EXT=$(sed -n 's/^Source:[ \t]*%{name}-%{version}\.\([a-z\.]*\)$/\1/p' $SPEC)
TARBALL=$PROJECT-$VERSION.$EXT

usage() {
    [ -n "$@" ] && echo -e "$@\n" >&2
    cat >&2 <<EOF
Usage: $0 [-h]

Relink tarball to match the version in $SPEC.
EOF
    exit 1
}

quit() {
    echo "$@" >&2
    exit 0
}

run() {
    echo "$@" >&2
    eval "$@" || exit 1
}

[ "$1" == "-h" ] && usage
[ -z "$VERSION" ] && usage "couldn't determine version in $SPEC"
[ -z "$EXT" ] && usage "couldn't determine source extension in $SPEC"
[ -e $TARBALL ] && quit "$TARBALL exists, nothing to do"

[ -e "$SRCDIST/$TARBALL" ] || quit "$SRCDIST/$TARBALL does not exist, exiting" 

[ -h $PROJECT-*.$EXT ] && run rm -v "$PROJECT-*.$EXT"

run ln -vs "$SRCDIST/$TARBALL"

quit "update $PROJECT.changes now!"
