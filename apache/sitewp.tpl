# Place any notes or comments you have here
# It will make any customisation easier to understand in the weeks to come

# domain: domain1.com
# public: /var/www/domain1.com/

<VirtualHost *:80>

 # Admin email, Server Name (domain name) and any aliases
 ServerAdmin webmaster@domain1.com
 ServerName  %(server_name)s
 ServerAlias www.%(server_name)s


 # Index file and Document Root (where the public files are located)
 DirectoryIndex index.php
 DocumentRoot %(project_path)s
<directory %(project_path)s>
AllowOverride All
</directory>


 # Custom log file locations
 LogLevel warn
 ErrorLog  /var/log/www/%(server_name)s.error.log
 CustomLog /var/log/www/%(server_name)s.access.log combined

</VirtualHost>

