#!/bin/bash
PASSWORD="%(db_pass)s"
USERNAME="%(db_user)s"
/srv/backup-scripts/automysqlbackup-ui.sh $PASSWORD $USERNAME
/srv/backup-scripts/br-apache.sh -w 0 -b /srv/backup/data

