#!/bin/sh
# full and incremental backup script
# created 07 February 2000
# Based on a script by Daniel O'Callaghan <danny@freebsd.org>
# and modified by Gerhard Mourani <gmourani@videotron.ca>

#Change the 5 variables below to fit your computer/backup

COMPUTER=userinspired                           # name of thiscomputer
DIRECTORIES="/srv/backup/data"                     	# directoris to backup
BACKUPDIR=/srv/backup/periodic                     	# where to store the backups
TIMEDIR=/srv/backup-scripts          # where to store timeoffullbackup
TAR=/bin/tar                            	# name and locaction of tar

#You should not have to change anything below here

PATH=/usr/local/bin:/usr/bin:/bin
DOW=`date +%a`              		# Day of the week e.g. Mon
DOM=`date +%d`              		# Date of the Month e.g. 27
DM=`date +%d%b`             	# Date and Month e.g. 27Sep

# On the 1st of the month a permanet full backup is made
# Every Sunday a full backup is made - overwriting last Sundays backup
# The rest of the time an incremental backup is made. Each incremental
# backup overwrites last weeks incremental backup of the same name.
#
# if NEWER = "", then tar backs up all files in the directories
# otherwise it backs up files newer than the NEWER date. NEWER
# gets it date from the file written every Sunday.
if [ -f $TIMEDIR/$COMPUTER-full-date ]; then


# Monthly full backup
if [ $DOM = "01" ]; then
        NEWER=""
        $TAR $NEWER -czf $BACKUPDIR/$COMPUTER-$DM.tar.gz $DIRECTORIES
fi

# Weekly full backup
if [ $DOW = "Sun" ]; then
        NEWER=""
        NOW=`date +%d-%b`

        # Update full backup date
        echo $NOW > $TIMEDIR/$COMPUTER-full-date
        $TAR $NEWER -czf $BACKUPDIR/$COMPUTER-$DOW.tar.gz $DIRECTORIES

# Make incremental backup - overwrite last weeks
else

        # Get date of last full backup
        NEWER="--newer `cat $TIMEDIR/$COMPUTER-full-date`"
        $TAR $NEWER -czf $BACKUPDIR/$COMPUTER-$DOW.tar.gz $DIRECTORIES
fi

else

 mkdir /$TIMEDIR
 date +%d-%b > /$TIMEDIR/$COMPUTER-full-date
fi

