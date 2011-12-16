#!/bin/sh

EXTRACTOR_BASE="/home/murawaki/research/mediasiki"
SCRIPT="python $EXTRACTOR_BASE/scripts/parse_dump.py"
TITLE=$1
DB=$2
if [ ! -f "$TITLE" -o ! -d "$DB" ]; then
    echo usage $0 title 1>&2
    exit 1
fi

l=`cat $TITLE | wc -l`
task_num=`expr $l / 1000`
task_num=`expr $task_num + 1`
for ((i=0;i<$task_num;i+=1)); do
    task_name=`printf dump%03d $i`
    start=`expr $i '*' 1000`
    end=`expr $start + 999`
    echo "$SCRIPT --input=$TITLE --db=$DB --plain --start=$start --end=$end > $task_name"
done
