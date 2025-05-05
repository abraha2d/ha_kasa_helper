#!/usr/bin/env bash

# $SCRIPTS should be setup by whichever script sourced this file
ROOT=$(dirname "${SCRIPTS}")
export ROOT

source() {
  local f="$1"
  shift
  builtin source "${f}" "${@}"
}

get_pixi() {
  if [[ -z "$PIXI_EXE" ]]; then
    PIXI_EXE=$(command -v pixi || :)
  fi

  if [[ ! -x "$PIXI_EXE" ]]; then
    export PIXI_HOME=$ROOT/.pixi
    PIXI_EXE=$PIXI_HOME/bin/pixi
  fi

  if [[ ! -x "$PIXI_EXE" ]]; then
    export PIXI_NO_PATH_UPDATE=1
    export PIXI_VERSION=latest
    curl -fsSL https://pixi.sh/install.sh | bash >&2
  fi

  if [[ ! -x "$PIXI_EXE" ]]; then
    echo "Something went wrong when trying to pixi. Aborting..."
    exit 1
  fi

  echo "${PIXI_EXE}"
}
