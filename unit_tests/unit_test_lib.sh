#takes a command executes it and check its return value
exec_n_test () {
    echo -n "checking success of $1 ... "
    "$@" > ent.trace 2>&1 
    if test $? != "0"
	then
	echo "fail with trace :"
	cat ent.trace
	exit 1
      else
	echo "success"
    fi
}

checkretstr () {
    echo -n "checking retstr $1 against result of $2 command ... "
    WAITED=$1
    shift
    $@ > ent.trace 2>&1
    RETSTR=`cat ent.trace | awk -F= '{ print $3 }'`
    if test a$RETSTR != a$WAITED
        then
        echo "fail with trace :"
        cat ent.trace
        rm ent.trace
        exit 1
      else
        echo "success"
	rm -f ent.trace
    fi
}

exec_n_test_fail () {
    echo -n "checking failure of $1... "
    $@ 2>&1 > ent.trace 
    if test $? != "0"
	then
	    echo "success"
	    rm -f ent.trace
	else
	    echo "not failed"
            cat ent.trace
            rm -f ent.trace 
            exit 1
    fi
}

check_equal_files () {
    echo -n "check equal files $1 $2..."
    diff -q $1 $2 > /dev/null 2>&1 
    if test $? -eq 0
    then
        echo "success"
    else
        echo "fail : files are different"
        exit 1
    fi
}

check_diff_files () {
    echo -n "check diff files $1 $2..."
    diff -q $1 $2  > /dev/null 2>&1 
    if test $? -eq 0
    then
        echo "fail : files are equal"
        exit 1
    else
        echo "success"
    fi
}

check_exist_file () {
    echo -n "check existence of $1..."
    if test -f $1
    then
        echo "success"
    else
        echo "fail : the file does not exist: $1"
        exit 1
    fi
}

check_empty_file () {
    echo -n "check emptyness of $1..."
    nbc=`cat $1 | wc -c`
    if test ${nbc} -eq 0
    then
        echo "success"
    else
        echo "fail : the file has size : ${nbc}"
        exit 1
    fi
}

check_not_empty_file () {
    echo -n "check non emptyness of $1..."
    nbc=`cat $1 | wc -c`
    if test ${nbc} != "0"
    then
        echo "success"
    else
        echo "fail : the file is empty"
        exit 1
    fi
}


check_equal_values () {
    echo -n "check equality of $1 $2..."
    if test $1 = $2
    then
        echo "success"
    else
        echo "fail : values are different"
        exit 1
    fi
}  

clean_all () {
    kill_pyrame.sh > /dev/null 2>&1 
    rm -f *.trace running*.*raw test*.*raw > /dev/null 2>&1 
}
