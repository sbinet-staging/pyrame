. /opt/pyrame/ports.sh
if test $# -lt 1
then
echo "usage $0 varname"
exit 1
fi
chkpyr2.py localhost $VARMOD_PORT getvar_varmod "0" $1 
