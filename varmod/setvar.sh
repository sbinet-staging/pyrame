. /opt/pyrame/ports.sh
if test $# -lt 2
then
echo "usage $0 varname value"
exit 1
fi
chkpyr2.py localhost $VARMOD_PORT setvar_varmod  "0" $1 $2 