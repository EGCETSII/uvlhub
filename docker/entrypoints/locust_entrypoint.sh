#!/bin/sh
# Locust entrypoint.
#
# If the caller didn't supply a -f / --locustfile, default to the bootstrap
# that ships with splent_framework. This used to live in core/bootstraps/, but
# now that the framework is a pip dependency the actual path lives somewhere
# under site-packages — resolve it at runtime instead of hardcoding.
set -e

case " $* " in
    *" -f "*|*" --locustfile "*)
        exec locust "$@"
        ;;
esac

BOOTSTRAP=$(python -c 'import splent_framework.bootstraps.locustfile_bootstrap as m; print(m.__file__)')
exec locust -f "$BOOTSTRAP" "$@"
