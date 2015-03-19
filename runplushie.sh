#!/bin/sh

export PYTHONPATH="${PYTHONPATH}:../NEaBLib/"

args=( "$@" )
for i in ${!args[@]}
do
    if [ "${args[$i]}" == "-c" -o "${args[$i]}" == "--console" ]
    then
        cd loop
        python testconsole.py &
        cd ../
        unset args[$i]
    fi
done

python botrunner.py "${args[@]}"
