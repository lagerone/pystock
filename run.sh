#!/bin/bash

# silent pushd & popd, https://stackoverflow.com/a/25288289/975720
pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

# All args except the first
TICKERS=${@:1}

if [ -z "$TICKERS" ]; then
  TICKERS=AMC
fi

SCRIPT=`readlink -f "$0"`
SCRIPT_PATH=`dirname $SCRIPT`

pushd $SCRIPT_PATH
source venv/bin/activate
python src/main.py $TICKERS
deactivate
popd