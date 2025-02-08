#!/bin/bash

[ -z "$CLONE_DIR" ] && echo "Need to set CLONE_DIR to create and clone code into" && exit 8;
[ -z "$GIT_URL" ] && echo "Need to set GIT_URL" && exit 8;
[ -z "$COMMIT_HASH" ] && echo "Need to set COMMIT_HASH" && exit 8;

PWD=`pwd`

rm -rf $CLONE_DIR
mkdir -p $CLONE_DIR
cd $CLONE_DIR

git init || exit 8
git remote add origin "$GIT_URL" || exit 8
git fetch origin --depth 1 || exit 8
git branch || exit 8
git fetch --depth 1 origin $COMMIT_HASH || exit 8
git checkout -f "$COMMIT_HASH"  || exit 8

cd $PWD
