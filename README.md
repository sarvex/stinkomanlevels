## Custom Stinkoman Levels

This is something I made back in high school, so don't expect top quality.
[www.stinkomanlevels.com](http://www.stinkomanlevels.com/)

### Installation

  * Linux
  * Install
    * mysql-server 
    * Django 1.2.2
    * Apache
    * python-mysqldb
  * Add config to Apache:

    ```
    WSGIScriptAlias / /home/andy/stinkomanlevels/wsgi.py

    Alias /media "/home/andy/stinkomanlevels/media"
    <Directory /media>
            Options FollowSymLinks
            AllowOverride None
            SetHandler None
    </Directory>
    ```
  * chmod -R o+rwx /home/andy/stinkomanlevels
