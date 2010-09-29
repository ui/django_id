# Configuration file for varnish
#
# /etc/init.d/varnish expects the variables $DAEMON_OPTS, $NFILES and $MEMLOCK
# to be set from this shell script fragment.
#

# Maximum number of open files (for ulimit -n)
NFILES=131072

# Maximum locked memory size (for ulimit -l)
# Used for locking the shared memory log in memory.  If you increase log size,
# you need to increase this number as well
MEMLOCK=82000

# Default varnish instance name is the local nodename.  Can be overridden with
# the -n switch, to have more instances on a single server.
INSTANCE=$(uname -n)

# This file contains 4 alternatives, please use only one.

# Listen on specify port, administration on localhost:6082, and forward to
# one content server selected by the vcl file, based on the request.  Use a 1GB
# fixed-size cache file.
#
DAEMON_OPTS="-a :%(port_number)s \
             -T localhost:6082 \
             -f /etc/varnish/default.vcl \
             -s file,/var/lib/varnish/$INSTANCE/varnish_storage.bin,1G"

