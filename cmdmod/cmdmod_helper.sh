#!/bin/bash

function submod_setres {
    echo "+_+setres+_+($1,\"$2\")"
}

function submod_execcmd {
    echo "+_+execcmd+_+($# "$@" )"
    read RES
    export RETCODE=`echo $RES | awk -F, '{ print $1 }'`
    export RETSTR=`echo $RES | awk -F, '{for (i=2; i<=NF; i++) print $i}'`
}

function internal_execcmd {
    #echo "internal_execcmd printing"
    "$@"
    echo "++_++"
}
