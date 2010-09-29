#!/bin/bash


# NOTE: run this script as root to make sure ownership and permission 
# are correctly preserved.

# Direktori utama yang berisi subdirektori konfigurasi, log dan 
# module milik Apache. Direktori ini disesuaikan dengan 
# nilai directive ServerRoot

APACHE_PATH=/etc/apache2/

# nama file konfigurasi utama Apache. 
MAIN_CONFIG_NAME=apache2.conf

# Direktori yang akan menampung hasil backup
BACKUP_PATH=/home/ui-backup/data-backup

# just in case someday we want to restore logs, aliases and web content to
# somewhere else
ALT_ROOT=""

# 0:backup, 1:restore
OPERATION=""

TODAY_TIME="apache"

#----------------------------------------------------------------------
#backup
#----------------------------------------------------------------------
function backup ()
{
    mkdir -p  $BACKUP_PATH/$TODAY_TIME/{www,conf,logs,aliases}
    cp -a -T $APACHE_PATH/ $BACKUP_PATH/$TODAY_TIME/conf/

    list_include=( $(grep -E -w -r -h "^[[:space:]]*Include" $APACHE_PATH/$MAIN_CONFIG_NAME | grep -v \# | awk '{print $2 }' )  );

    if [[ -d $APACHE_PATH/sites-available && -r  $APACHE_PATH/sites-available ]];
    then
	    list_include2=( $(find $APACHE_PATH/sites-available/ -type f )  );
    fi;


    for a in $APACHE_PATH/$MAIN_CONFIG_NAME ${list_include[@]} ${list_include2[@]}
    do 
	    if [ ${a:0:1} == "/" ]
	    then 
		    path_conf=$a
	    else
		    path_conf=$APACHE_PATH/$a
	    fi
	    echo "path conf $path_conf"
	    source_www=$(grep -E -w -r -h "^[[:space:]]*DocumentRoot" $path_conf | grep -v \# |  awk '{print $2}')
	    source_www2=( ${source_www//\"/} )

	
        for b in $(seq 0 $((${#source_www2[@]}-1)))
        do
            echo "source www: ${source_www2[$b]} "
            mkdir -p  $BACKUP_PATH/$TODAY_TIME/www/${source_www2[$b]}
            cp -a -T ${source_www2[$b]}/ $BACKUP_PATH/$TODAY_TIME/www/${source_www2[$b]}
            
        done

        alias_dir=$(grep  -E -r -w -h "^[[:space:]]*Alias"\|"^[[:space:]]*ScriptAlias" $path_conf | grep -v \# | awk '{print $3}')
        alias_dir2=( ${alias_dir//\"/} )

        
        for b in $(seq 0 $((${#alias_dir2[@]}-1)))
        do
            echo "alias dir : ${alias_dir2[$b]} "
            if [ -d  ${alias_dir2[$b]} ]
            then
                mkdir -p  $BACKUP_PATH/$TODAY_TIME/aliases/${alias_dir2[$b]}
                cp -a -T ${alias_dir2[$b]}/ $BACKUP_PATH/$TODAY_TIME/aliases/${alias_dir2[$b]}
            else
                
                mkdir -p  $BACKUP_PATH/$TODAY_TIME/aliases/$(dirname ${alias_dir2[$b]})
                cp -a ${alias_dir2[$b]} $BACKUP_PATH/$TODAY_TIME/aliases/${alias_dir2[$b]}
            fi
            
        done

        
        log_dir=$(grep  -E -r -w -h "^[[:space:]]*ErrorLog"\|"^[[:space:]]*CustomLog" $path_conf | grep -v \# | awk '{print $2}')
        log_dir2=( ${log_dir//\"/} )

        
        for b in $(seq 0 $((${#log_dir2[@]}-1)))
        do
            if [ ${log_dir2[$b]:0:1} == "/" ]
            then 
                log_dir3=${log_dir2[$b]}
            else
                log_dir3=$APACHE_PATH/${log_dir2[$b]}
            fi
            echo "log dir : $log_dir3 "
            mkdir -p  $BACKUP_PATH/$TODAY_TIME/logs/$(dirname $log_dir3)
            cp -a -T $(dirname $log_dir3) $BACKUP_PATH/$TODAY_TIME/logs/$(dirname $log_dir3)
            
        done
    done;
}

#----------------------------------------------------
#restore part
#----------------------------------------------------

function restore ()
{
    echo "Found following saved Apache configuration"
    echo "Format : YYYY-MM-DD-hhmm"
    echo
    find $BACKUP_PATH -mindepth 1  -maxdepth 1 -type d -exec basename {} \;

    echo "Pilihan anda?"
    read SELECTED_PATH

    if [[ -d $BACKUP_PATH/$SELECTED_PATH && -r $BACKUP_PATH/$SELECTED_PATH ]];
    then 
        echo "directory is exist and readable";
        echo
    else 
        echo "directory is not exist and/or not readable";
        exit 2;
    fi

    echo "You have selected to restore from: "
    echo "$BACKUP_PATH/$SELECTED_PATH"
    echo
    echo "The main configuration files will be restored to: "
    echo "$APACHE_PATH"
    echo
    echo "The rest of the files (logs, aliases, web content) will be restored"\
        "to the respective directory e.g logs go to /var/log/apache2"
    echo "If any files with the same name found in the destination directories,"\
        "IT WILL BE SIMPLY OVERWRITTEN!!!"
    echo
    read -n 1  -p "Are you sure to do it [y/n]? " USER_RESPONSE
    if ! [[ $USER_RESPONSE == "y" ||  $USER_RESPONSE == "Y" ]]
    then
        echo -e "\nExiting..."
        exit 3;
    fi

    echo
    echo "Restoring saved files...."
    rsync -aPH -K  $BACKUP_PATH/$SELECTED_PATH/conf/ $APACHE_PATH/

    rsync -aPH -K $BACKUP_PATH/$SELECTED_PATH/aliases/ $ALT_ROOT/
    rsync -aPH -K $BACKUP_PATH/$SELECTED_PATH/logs/ $ALT_ROOT/
    rsync -aPH -K $BACKUP_PATH/$SELECTED_PATH/www/ $ALT_ROOT/

    echo "Done"
}

#----------------------------------------------------------------------
# main part
#----------------------------------------------------------------------

if [[ EUID -ne 0 ]];
then
	echo "Script tidak dijalankan sebagai root"
	echo "Exiting...."
	exit 1;
fi

while getopts "o:b:c:w:h" Option
do
    case $Option in
        b ) if [[ -d "$OPTARG" && -r "$OPTARG" ]] ; 
                then BACKUP_PATH="$OPTARG"; 
                echo "BACKUP_PATH = $BACKUP_PATH";
            fi;;
        o ) if [[ -d "$OPTARG" && -r "$OPTARG" ]] ; 
                then APACHE_PATH="$OPTARG"; 
                echo "APACHE_PATH = $APACHE_PATH";
            fi;;
        c ) if [[ -f "$OPTARG" && -r "$OPTARG" ]] ; 
                then MAIN_CONFIG_NAME="$OPTARG"; 
                echo "MAIN_CONFIG_NAME = $MAIN_CONFIG_NAME";
            fi;;

        w ) if [[ $OPTARG -eq 0 ]];
                then OPERATION="backup";
            elif [[ $OPTARG -eq 1  ]];
                then OPERATION="restore";
            fi;;

        h ) 
            echo "-o defines the directory name that holds your" \
                 "Apache configuration files"
            echo
            echo "-b defines the directory where you want to back-up the Apache" \
                 "configuration files"
            echo
            
            echo "-w decides whether this script will do backup ("0")"
            echo "or restore ("1"). You have to choose, otherwise this script"
            echo "will terminate itself"
            
            echo "During backup, files will be copied from ServerRoot and"
            echo "related directories to the directory you define via -b switch"
            echo "or the one you set in BACKUP_PATH variable."
            echo
            echo "On the other hand, during restore, files will be copied from"
            echo "the directory you define via -b switch or BACKUP_PATH variable"
            echo "back to the directory mentioned in -o switch and related directories."
            echo
            echo "-c lets you define the name of main Apache configuration file." \
                 "In most distros, it's either apache2.conf or httpd.conf."
            echo
            echo "It will be searched right under the directory you define via -o option" \
                 "or by directly tweaking APACHE_PATH variable (only relevant during backup)".
            exit 0;
    esac
done

if [[ -z $OPERATION ]]
    then echo "Please specify whether you want to do backup or restore"
         echo "by using -w switch."
         exit 0;
fi;

if [[ $OPERATION == "backup" ]]
then
    backup;
else
    restore;
fi;

