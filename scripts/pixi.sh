#!/usr/bin/env bash

set -e

SCRIPTS=$(readlink -f "$(dirname "$0")")
# shellcheck source-path=SCRIPTDIR/utils.sh
. "${SCRIPTS}"/utils.sh

exec $(get_pixi) "$@"
