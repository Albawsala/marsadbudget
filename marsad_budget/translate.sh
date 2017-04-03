#!/bin/bash

CWD=/home/user0/www/marsad_budget

case $1 in
	extract)
	pybabel extract -F $CWD/babel.cfg -o $CWD/messages.pot $CWD
	pybabel update -i $CWD/messages.pot -d $CWD/translations
	;;

	compile)
	pybabel compile -d $CWD/translations
	;;

	*)
	echo "usage: `basename $0` {extract|compile}"
esac
