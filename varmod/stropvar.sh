. /opt/pyrame/ports.sh
if test $# -lt 3
then
echo "usage $0 varname op:c(concat) value"
exit 1
fi
chkpyr2.py localhost $VARMOD_PORT stropvar_varmod "0" $1 $2 $3
