#!/bin/bash
. /opt/pyrame/cmdmod_helper.sh

function void_test {
    echo "inside bash void code"
    submod_setres 1 "void()"
}

function fail_test {
    submod_setres 0 "fail()"
}

function onearg_test {
    if test $# != "1" 
    then
        submod_setres 0 "1 arg needed : $# provided"
    else
        submod_setres 1 "onearg($1)"
    fi
}

function twoargs_test {
    if test $# != "2" 
    then
        submod_setres 0 "2 arg needed : $# provided"
    else
        submod_setres 1 "twoargs($1,$2)"
    fi
}

function varmod_test {
    submod_execcmd "setvar_varmod" "0" "x" "2"
    echo "varmod_test retcode : $RETCODE"
    echo "varmod_test retstr : $RETSTR"
    if test $RETCODE != "1"
    then
        submod_setres 0 "cant exec setvar : $RETSTR"
    else
        submod_setres 1 "ok"
    fi
}
