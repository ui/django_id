from __future__ import with_statement
from fabric.api import env, run, local, sudo, put, prompt, settings, get
from fabric.contrib.project import rsync_project, upload_project
from fabric.contrib.files import append, upload_template, sed
from fabric.context_managers import cd
from fabric.operations import local
from time import strftime
from getpass import getpass
import platform
import os, site, sys

GIT_BRANCH ='fabfile'

PROJECT_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__))).lower()
PROJECT_PATH = '/var/www/%s/' % PROJECT_NAME

APPLICATION_PATH = '%sproject/' % PROJECT_PATH

REQUIREMENTS_FILE = "%srequirements.txt" % APPLICATION_PATH
HOME_PATH = ('/home/%s/' % env.user)
    
TIME = strftime("%Y-%m-%d-%H-%M")
PROJECT_NAME_TIME = ('project-%s' % TIME)


def restart():
    "Reboot Apache2 server."
    sudo("apache2ctl graceful")

def update_os():
	sudo('apt-get update && apt-get upgrade -y')

def setup_os():
	update_os()
	sudo('apt-get install python-setuptools python-dev build-essential subversion libmysqlclient-dev libapache2-mod-python libapache2-mod-wsgi libjpeg-dev git-core mercurial -y')
	sudo('easy_install -U pip')
	sudo('pip install django')
	sudo('pip install MySQL-python')
	sudo('pip install PIL')
	sudo('pip install django-debug-toolbar')

def setup_virtual_env():
	sudo('pip install virtualenv')
	with cd(PROJECT_PATH):
		sudo('virtualenv env')
		with cd('env'):
			run('source bin/activate')
	install_project_requirements()

def install_project_requirements():
	sudo('pip install -E %senv -r %s' % (PROJECT_PATH, REQUIREMENTS_FILE))

def setup():
    setup_os()
    setup_virtual_env()

def setup_apache(TEMPLATE):
	server_name = prompt('Enter server name:', 'server_name')	
	upload_template(
		'apache/%s' %TEMPLATE,
		HOME_PATH,
		context = {
			'server_name': server_name,
			'project_path': PROJECT_PATH,
			'project_name': PROJECT_NAME,
		}
	)
	sudo('mv %s /etc/apache2/sites-available/%s' % (TEMPLATE, PROJECT_NAME))
	sudo('a2ensite %s' %PROJECT_NAME)
	sudo('mkdir -p /var/log/www')
	restart_apache()
'''
def setup_apache():
	o = open("%s.com" % PROJECT_NAME,"a")
	for line in open("apache/site.txt"):
		line = line.replace("<server-name>","%s" % SERVER_NAME)
		line = line.replace("<project_env>","%s" % APPLICATION_PATH)
		o.write(line)
	o.close()
	
	put('%s.com' % PROJECT_NAME, HOME_PATH )
	sudo('mv %s%s.com /etc/apache2/sites-available/' %(HOME_PATH, PROJECT_NAME))
	local('rm %s.com' % PROJECT_NAME)
	#sudo('mv /etc/apache2/sites-available/site.conf /etc/apache2/sites-available/%s' % PROJECT_NAME)
	sudo('a2ensite %s.com' %PROJECT_NAME)
	sudo('mkdir -p /var/log/www')
	restart_apache()
'''
def restart_apache():
	sudo('/etc/init.d/apache2 restart')

def restart_mysql():
	sudo('/etc/init.d/mysql restart')
    
def deploy_project():
	#upload_app()
	#extract_app()
	if not os.path.exists("%s" % PROJECT_PATH):
		upload_project()
		with cd(PROJECT_PATH):
			sudo('ln -s project-%s project' % TIME)
			sudo('cp -R project/media .')
			sudo('chown -R www-data media')
			sudo('chgrp -R www-data media')
		setup_virtual_env()
		setup_apache("site.conf.tpl")
	else:
		print"project ini telah dibuat sebelumnya"
def upload_project(remote_dir = HOME_PATH, exclude = ['.git', '*.pyc', 'settings_local.py'], delete = False):
	rsync_project(HOME_PATH, exclude = exclude, delete = delete)
	sudo('mkdir -p %s' % PROJECT_PATH)
	sudo("cp -R %s %sproject-%s" % (PROJECT_NAME, PROJECT_PATH, TIME))
	sudo('ls %s | grep project-%s >> %srevisions.log' %(PROJECT_PATH, TIME, PROJECT_PATH))
	sudo('echo "project-%s" > %scurrent_revision.log' %(TIME, PROJECT_PATH))

def deploy():
	setup_os()
	deploy_project()

'''	
def upload_app():
	local('git archive --format=tar %s | gzip > %s.tar.gz' % (GIT_BRANCH, PROJECT_NAME))
	put('%s.tar.gz' % PROJECT_NAME, HOME_PATH)
	local('rm %s.tar.gz' % PROJECT_NAME)

def extract_app():
	with cd(HOME_PATH):
		run('mkdir -p project-%s' % TIME) 
		run('cp %s.tar.gz project-%s/' %(PROJECT_NAME, TIME) )
		with cd(PROJECT_NAME_TIME):
			run('tar xfvz %s.tar.gz' % PROJECT_NAME)
			run('rm %s.tar.gz' % PROJECT_NAME)
	sudo('mkdir -p /var/www/%s/' % PROJECT_NAME)
	sudo('mv %sproject-%s %s' % (HOME_PATH, TIME, PROJECT_PATH) )
	sudo('ls %s | grep project-%s >> %srevisions.log' %(PROJECT_PATH, TIME, PROJECT_PATH))
'''
def update_project(app_requirements= False):
	upload_project()
	with cd(PROJECT_PATH):
		sudo('cp project/settings_local.py project-%s' % TIME)
		sudo('rm -R project')
		sudo('ln -s project-%s project' % TIME)
		sudo('cp -R project/media .')
		sudo('chown -R www-data media')
		sudo('chgrp -R www-data media')
	if app_requirements == True:
		install_project_requirements()
	restart_apache()

def backup(db_pass, db_user):
	with cd("/srv"):
		sudo("mkdir -p backup")
	put('backup/Automysqlbackup-ui.sh', HOME_PATH)
	put('backup/br-apache.sh', HOME_PATH)
	o = open("backup/backup2.sh","a")
	for line in open("backup/backup.sh"):
		line = line.replace("<db_pass>","%s" %db_pass)	
		line = line.replace("<db_user>","%s" %db_user)
		o.write(line)
	o.close()
	sudo("mv Automysqlbackup-ui.sh /srv/backup/")
	sudo("mv br-apache.sh /srv/backup/")
	put('backup/backup2.sh', HOME_PATH)
	sudo("mv backup2.sh /srv/backup/")
	sudo("mv /srv/backup/backup2.sh /srv/backup/backup.sh")
	sudo ("chmod +x /srv/backup/backup.sh")
	local('rm backup/backup2.sh')
	sudo('echo "00 1    8 * *   root    /srv/backup/backup.sh" >> /etc/crontab')
	
	
def setup_backup_client():
	"""Sets up target host to do automatic daily Apache and MySQL backup"""
	prompt('Database user for mysql:', 'db_user')
	env.db_pass = getpass('Database password for mysql:')	
	sudo("mkdir -p /srv/backup/data")
	sudo("mkdir -p /srv/backup/periodic")
	sudo("mkdir -p /srv/backup-scripts")

	#Upload necessary templates and backup scripts
	upload_template(
	    'backup/backup.sh.tpl', 
	    HOME_PATH, 
	    context = {
	        'db_user' : env.db_user,
	        'db_pass' : env.db_pass,
	    }
	)
	
	put('backup/automysqlbackup-ui.sh', HOME_PATH)
	put('backup/br-apache.sh', HOME_PATH)	
	put('backup/last-full/userinspired-full-date', HOME_PATH)
	put('backup/periodic.sh', HOME_PATH)
	sudo("mv automysqlbackup-ui.sh /srv/backup-scripts/")
	sudo("mv br-apache.sh /srv/backup-scripts/")
	sudo("mv backup.sh.tpl /srv/backup-scripts/backup.sh")
	sudo("mv periodic.sh /srv/backup-scripts/")
	sudo("mkdir -p /srv/backup-scripts/last-full")
	sudo("mv userinspired-full-date /srv/backup-scripts/last-full")
	sudo("chmod +x /srv/backup-scripts/*.sh")
	
	append('00 1    * * *   root    /srv/backup-scripts/backup.sh', '/etc/crontab', use_sudo = True)    
	append('00 2    * * *   root    /srv/backup-scripts/periodic.sh', '/etc/crontab', use_sudo = True)



def setup_backup_server():
	HOST = prompt('Hostname or IP address that you want to backup:', 'HOST')
	SERVER_NAME = prompt('Name of the server:', 'SERVER_NAME')
	time = prompt('Time for backup to be executed (ex: 00 5)','time')
	sudo("mkdir -p /srv/backup-server")
	sudo("chown ui-backup /srv/backup-server")
	append('%s * * *     ui-backup     rsync --delete -azvv -e ssh ui-backup@%s:/srv/backup/ /srv/backup-server/%s'%(time, HOST, SERVER_NAME), '/etc/crontab', use_sudo = True)

def transfer_project(remote_dir = HOME_PATH, exclude = ['.git', '*.pyc', 'settings_local.py'], delete = False):
    rsync_project(HOME_PATH, exclude = exclude, delete = delete)





#Minor Varnish utilities
def varnish_stats(port = 6082):	
    """Executes a stats command on varnish"""
    run('exec 9<>/dev/tcp/localhost/%(port)s ; echo -e "stats\nquit" >&9; cat <&9' % locals())

def flush_varnish(port = 6082, expression = ".*"):	
    """Purge cached items in varnish"""
    run('exec 9<>/dev/tcp/localhost/%(port)s ; echo -e "url.purge %(expression)s\nquit" >&9; cat <&9' % locals())

def setup_varnish():
	sudo('apt-get install varnish -y')
	port_number = prompt('Enter port number[6081]:', 'port_number')
	upload_template(
		'varnish/varnish.tpl',
		HOME_PATH,
		context = {
			'port_number' : port_number,
		}
	)
	sudo('rm /etc/default/varnish')
	sudo('mv varnish.tpl /etc/default/varnish')

def restart_varnish():
	sudo('/etc/init.d/varnish restart')
#Minor memcached utilities
def memcached_stats(port = 11211):	
    """Executes a stats command on memcached"""
    run('exec 9<>/dev/tcp/localhost/%(port)s ; echo -e "stats\nquit" >&9; cat <&9' % locals())


def restart_memcached():
	sudo ('/etc/init.d/memcached stop && sudo /etc/init.d/memcached start')		
	
	
def flush_memcached(port = 11211, seconds = 0):
    """ Flushes all memcached items """
    run('exec 9<>/dev/tcp/localhost/%(port)s ; echo -e "flush_all %(seconds)s\nquit" >&9; cat <&9' % locals())
    
    
def backup_mysql(db_user = 'root', db_pass=None, database='--all-databases'):
    '''Backup MySQL database(s)'''
    db_user = prompt('Database user to connect with [root]:') or 'root'
    env.db_pass = getpass('Database password to connect with []:')
    databases = prompt('Databases to backup [all]:') or '--all-databases'
    db_pass = '-p%s' % env.db_pass if env.db_pass else ''
    outfile = '%s-%s-%s.sql.gz' % (env.host, databases.lstrip('--').replace(' ', '_'), TIME) 
    run('mysqldump --opt -u %(db_user)s %(db_pass)s --databases %(databases)s | gzip > /tmp/%(outfile)s' % locals())
    get('/tmp/%(outfile)s' % locals(), '%(outfile)s' %locals())
    run('rm /tmp/%(outfile)s' % locals())


def mysql_move_tables(db_user = 'root', db_pass = None, database = '--all-databases'):
    """
    Move MySQL tables from local database to another.
    Steps to move tables:
    1. Dump tables from source database
    2. Rename tables to table_name_new
    3. Transfer tables to destination database host
    4. Import the tables
    5. Rename original tables to table_name_old in destination database
    6. Rename the new tables from table_name_new to table_name
    """
    db_user = prompt('Database user to connect with [root]:') or 'root'
    env.db_pass = getpass('Database password to connect with []:')
    db_pass = '-p%s' % env.db_pass if env.db_pass else ''
    db = prompt('Database name []:').strip()
    tables = prompt('Tables to move (separated by spaces) []:').strip().split()
    outfile = '/tmp/%s-%s.sql' % (db, '__'.join(tables))
    
    #All of this is done on localhost
    local('mysqldump --opt -u %s %s %s %s > %s' % (db_user, db_pass, db, ' '.join(tables), outfile))
    for table in tables:
        #Now we need to replace these lines
        local("sed -i.bak -r -e 's/DROP TABLE IF EXISTS `%s`/DROP TABLE IF EXISTS `%s`/g' %s" % (table, (table + '_new'), outfile))
        local("sed -i.bak -r -e 's/CREATE TABLE `%s`/CREATE TABLE `%s`/g' %s" % (table, (table + '_new'), outfile))
        local("sed -i.bak -r -e 's/LOCK TABLES `%s` WRITE/LOCK TABLES `%s` WRITE/g' %s" % (table, (table + '_new'), outfile))
        local("sed -i.bak -r -e 's/ALTER TABLE `%s`/ALTER TABLE `%s`/g' %s" % (table, (table + '_new'), outfile))
        local("sed -i.bak -r -e 's/INSERT INTO `%s` VALUES/INSERT INTO `%s` VALUES/g' %s" % (table, (table + '_new'), outfile))        
    local('cat %(outfile)s | gzip > %(outfile)s.gz' % locals())
    put('%s.gz' % outfile, '%s.gz' % outfile)
    
    #Now import the tables on destination host and rename
    run('gunzip < %s.gz | mysql -u %s %s %s' % (outfile, db_user, db_pass, db))
    rename_commands = ['ALTER TABLE %s RENAME %s_old;' % (table, table) for table in tables]
    rename_commands += ['ALTER TABLE %s_new RENAME %s;' % (table, table) for table in tables]
    rename_commands = ''.join(rename_commands)
    run('echo "use %s;%s" | mysql -u %s %s' % (db, rename_commands, db_user, db_pass))
    
# deploy word press project

def deploy_wp_project(remote_dir = HOME_PATH, exclude = ['.git','apache','fabfile.py','fabfile.pyc'], delete = False):
	if not os.path.exists("%s" % PROJECT_PATH):
		rsync_project(HOME_PATH, exclude = exclude, delete = delete)
		db_name = prompt('Enter db name:', 'db_name')
		db_user = prompt('Enter db user[root]:', 'db_user')
		db_pass = getpass('Database password:')
		run('sed -i "s/define(\'DB_NAME\',.*);/define(\'DB_NAME\', \'%s\');/" %sqi/wp-config.php' % (db_name, HOME_PATH))
		run('sed -i "s/define(\'DB_USER\',.*);/define(\'DB_USER\', \'%s\');/" %sqi/wp-config.php' %(db_user, HOME_PATH))
		run('sed -i "s/define(\'DB_PASSWORD\',.*);/define(\'DB_PASSWORD\', \'%s\');/" %sqi/wp-config.php' %(db_pass, HOME_PATH ))
		sudo('cp -R %s /var/www/%s' %(PROJECT_NAME, PROJECT_NAME))
		sudo('a2enmod rewrite')
		sudo('chown -R www-data %swp-content/uploads '% PROJECT_PATH)
		sudo('chgrp -R www-data %swp-content/uploads '% PROJECT_PATH)	
		setup_apache("sitewp.tpl")
		print "Anda harus melakukan import database anda sebelum mengakses ke website"
	else:
		print "Project ini telah dibuat sebelumnya"
		
	#upload_template(
	#	'apache/sitewp.tpl',
	#	HOME_PATH,
	#	context = {
	#		'server_name' : server_name,
	#		'project_name' : PROJECT_NAME,
	#	}
	#)
	#sudo('mv sitewp.tpl /etc/apache2/sites-available/%s' % PROJECT_NAME)
	#sudo('a2ensite %s' %PROJECT_NAME)
	
	#sudo('mkdir -p /var/log/www')


def upgrade_wordpress(upload_file="y"):
	upload_file = prompt('Do you want to download latest.tar.gz (y/n):', 'upload_file')
	if upload_file == "y":
		sudo('rm -f latest.tar.gz')
		run('wget http://wordpress.org/latest.tar.gz')
	run('mkdir -p ~/wpupgrade/%s' % TIME)
	run('mkdir -p ~/wpupgrade/bac/%s' % TIME)
	run('cp ~/latest.tar.gz ~/wpupgrade/%s'% TIME)
	run('tar -C ~/wpupgrade/%s -xzf ~/wpupgrade/%s/latest.tar.gz' % (TIME, TIME))
	run('cp -R %s \
	~/wpupgrade/bac/%s/' % (PROJECT_PATH,TIME))
	sudo('cp -R ~/wpupgrade/%s/wordpress/* \
	%s' % (TIME, PROJECT_PATH))
	sudo('chown -R  www-data %s' % PROJECT_PATH)
	sudo('rm -R ~/wpupgrade/%s' % TIME)
	print("\nNow visit http://%s/wp-admin to complete upgrade" % env.host)

def update_wp_project(remote_dir = HOME_PATH, exclude = ['.git','apache','fabfile.py','fabfile.pyc','wp-config.php'], delete = False):
	rsync_project(HOME_PATH, exclude = exclude, delete = delete)
	with cd(PROJECT_PATH):
		sudo('mv /wp-content/themes/%s %s-%s.bak' % (PROJECT_NAME, PROJECT_NAME, TIME))	
		sudo('cp ~/%s/wp-content/themes/%s /wp-content/themes/'%(PROJECT_NAME, PROJECT_NAME))
		restart_apache()

def backup_webserver():
	sudo('./srv/backup/backup.sh')

def rollback():
	get('%srevisions.log','revisions.log'% PROJECT_PATH)
	get('%scurrent.log','current_revision.log'% PROJECT_PATH)
	for rev in open("current.log"):
		current_revision = rev	
	i = 0
	revision = {}
	for line in open("revisions.log"):
		revision[i] = line
		if current_revision == revision[i]:
			if i == 0:
				print"no previous version"
			else:
				with cd(PROJECT_PATH):
					sudo('rm -R project')
					sudo('ln -s %s project' % revision[i-1].rstrip('\n'))	
					sudo('cp -R project/media .')
					sudo('chown -R www-data media')
					sudo('chgrp -R www-data media')
					sudo('echo "%s" > %scurrent_revision.log' %(revision[i-1].rstrip('\n'), PROJECT_PATH))					
		i = i+1
	local('rm current_revision.log')
	local('rm revisions.log')



