#!/bin/bash

[ -z "$CLONE_DIR" ] && echo "Need to set CLONE_DIR to create and clone code into" && exit 8;
[ -z "$GIT_URL" ] && echo "Need to set GIT_URL" && exit 8;
[ -z "$COMMIT_HASH" ] && echo "Need to set COMMIT_HASH" && exit 8;
[ -z "$PRIVATE_KEY_HASH" ] && echo "Need to set PRIVATE_KEY_HASH" && exit 8;

export SSH_SCRIPT=${SSH_SCRIPT:=/tmp/git_ssh}
export TMP_DIR=${TMP_DIR:=/tmp/key-info}
export PRIVATE_KEY_PATH=${PRIVATE_KEY_PATH:=$TMP_DIR/id-key.pem}

rm -rf $CLONE_DIR
mkdir -p $CLONE_DIR

rm -rf $TMP_DIR
mkdir -p $TMP_DIR

echo $PRIVATE_KEY_HASH | base64 -d > $PRIVATE_KEY_PATH
chmod 600 $PRIVATE_KEY_PATH

PWD=`pwd`

rm -rf $CLONE_DIR
mkdir -p $CLONE_DIR
cd $CLONE_DIR

#ssh-agent bash -c "ssh-add $PRIVATE_KEY_PATH; git clone $GIT_URL"

git init || exit 8
git remote add origin "$GIT_URL" || exit 8
ssh-agent bash -c "ssh-add $PRIVATE_KEY_PATH; git fetch origin --depth 1" || exit 8
git branch || exit 8
ssh-agent bash -c "ssh-add $PRIVATE_KEY_PATH; git fetch --depth 1 origin $COMMIT_HASH" || exit 8
ssh-agent bash -c "ssh-add $PRIVATE_KEY_PATH; git checkout -f $COMMIT_HASH"  || exit 8

cd $PWD

#################################################################################
#echo '#!/bin/bash' > $SSH_SCRIPT
#echo '' >> $SSH_SCRIPT
#echo "trap 'rm -f /tmp/.git_ssh.\$\$' 0" >> $SSH_SCRIPT
#echo '' >> $SSH_SCRIPT
#echo 'if [ "$1" = "-i" ]; then' >> $SSH_SCRIPT
#echo '    SSH_KEY=$2; shift; shift' >> $SSH_SCRIPT
#echo '    echo "GIT_TERMINAL_PROMPT=0 ssh -i $SSH_KEY -o StrictHostKeyChecking=no -oBatchMode=yes \$@" > /tmp/.git_ssh.$$' >> $SSH_SCRIPT
#echo '    chmod +x /tmp/.git_ssh.$$' >> $SSH_SCRIPT
#echo '    export GIT_SSH=/tmp/.git_ssh.$$' >> $SSH_SCRIPT
#echo 'fi' >> $SSH_SCRIPT
#echo '' >> $SSH_SCRIPT
#echo '[ "$1" = "git" ] && shift' >> $SSH_SCRIPT
#echo '' >> $SSH_SCRIPT
#echo '# Run the git command' >> $SSH_SCRIPT
#echo 'git "$@"' >> $SSH_SCRIPT
#
#chmod 755 $SSH_SCRIPT
#################################################################################

