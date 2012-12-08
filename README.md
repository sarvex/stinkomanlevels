### Installation

  * Linux
  * Install
    * mysql-server 
    * Django 1.2.2
    * Apache
  * Add config to Apache:

    ```
    WSGIScriptAlias / /path/to/stinkomanlevels/wsgi.py

    Alias /media "/home/andy/stinkomanlevels/media"
    <Directory /media>
            Options FollowSymLinks
            AllowOverride None
            SetHandler None
    </Directory>
    ```
