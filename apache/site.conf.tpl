<VirtualHost *:80>
    ServerName %(server_name)s
    ServerAlias www.%(server_name)s

    Alias /media/ %(project_path)smedia/

    # gzip compression.
	<IfModule mod_deflate.c>
		# html, xml, css, and js:
		AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css application/x-javascript text/javascript application/javascript application/json
		# webfonts and svg:
		<FilesMatch "\.(ttf|otf|eot|svg)$" >
			SetOutputFilter DEFLATE
		</FilesMatch>
	</IfModule>

	<Directory %(project_path)sproject/media>
        Order deny,allow
        Allow from all
		
		#Uncomment the mod_expires section to enable far future expiry date
		#<IfModule mod_expires.c>
		#	<FilesMatch "\.(js|css|png|gif|jpg|jpeg|ico|eot|woff|otf)$">
   		#		ExpiresActive On
   		#		ExpiresDefault "access plus 1 year"
		#	</FilesMatch>
		#</IfModule>
    </Directory>

    # Uncomment the line below if you want to use daemon mode
	#WSGIDaemonProcess %(project_name)s processes=10 threads=15 display-name=%(project_name)s
	WSGIScriptAlias / %(project_path)sproject/apache/django.wsgi
    <Directory %(project_path)sproject/apache>
        Order Allow,Deny
        Allow from all
    </Location>
    ErrorLog  %(project_path)slog/%(server_name)s.error.log
    CustomLog %(project_path)slog/%(server_name)s.access.log combined
</VirtualHost>
