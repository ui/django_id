#!/bin/bash
PASSWORD="<db_pass>"
USERNAME="<db_user>"
/srv/backup-scripts/Automysqlbackup-ui.sh $PASSWORD $USERNAME
/srv/backup-scripts/br-apache.sh -w 0 -b /srv/backup

