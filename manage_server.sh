#!/bin/bash

COMMAND="$1"
PYTHON=`/usr/bin/which python`
START_COMMAND=""
STOP_COMMAND=""

case $COMMAND in
	start)
		echo "Starting give.datalove server..."
		pgrep -f "$PYTHON $PWD/app.py" &> /dev/null
		if [[ $? -ne 0 ]]; then
			nohup  $PYTHON "$PWD/app.py" &> output.log  \
				&> /dev/null &
			if [[ $? -eq 0 ]]; then
				echo "done."
			fi
		else
			echo "failed."
		fi
	;;
	stop)
		echo "Stoping give.datalove server..."
		pkill -f "$PYTHON $PWD/app.py" &> /dev/null \
				&& echo "done." \
				|| echo "failed."
	;;
	restart)
		echo "Restarting give.datalove server..."
		pkill -f "$PYTHON $PWD/app.py" &> /dev/null \
				&& nohup  $PYTHON "$PWD/app.py" &> output.log  &> /dev/null &
		if [[ $? -eq 0 ]]; then
			echo "done."
		else
			echo "failed."
		fi
	;;
	*)
		echo "Usage: $0 {start|stop|restart}" 1>&2
	;;
esac
