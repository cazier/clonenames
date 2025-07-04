# Deployment

## General Notes
It took me a *really* long time to figure this out. I had some rather specific needs, which I'm sure made it harder, and I'm rather certain there are some ways to make it better, but regardless. Here you go. Please note that depending on what you have on your server, this may all be different. However, these exact steps worked for me on the server I've deployed.

## Requirements (For This Deployment)
- A webserver (I used a Digital Ocean droplet)
- Nginx (v 1.14.0)
- Eventlet (v 0.24.1)
- ufw (v 0.35)

## Steps
1. On your webserver, make sure you have a python3.7 environment with eventlet installed, and that your server has nginx.
2. Before changing any of your code, make sure that it still runs under debug mode.
3. Edit [web.py](web.py), in the `if __name__ == "__main__":` section to remove `debug=True`, and add any port not in use on your server. For example `port = u'1999'`. ([Line 141](https://github.com/cazier/clonenames/blob/master/web.py#L141))
4. Edit [socketio.html](templates/socketio.html) to replace `var socket = io('http://' + document.domain + ':' + location.port);` with your actual domain name. ([Line 3](https://github.com/cazier/clonenames/blob/master/templates/socketio.html#L3))
 __NOTE: Do not specify a port here, unless your deployed server will not be using 80/443.__
4. (OPTIONAL) Edit [scripts.html](templates/scripts.html) by removing the local hosting of your JS files, to pull from the various CDNs.
5. Create a service to run your file. See my [sample.service](sample.service) as an example. Save it in `/etc/systemd/system/sample.service`
    5a. Note that, provided eventlet is installed, flask-socketio comes with a deployment server built in. All that is necessary is to run the file. Hence, `ExecStart=[working_directory]/python web.py`
6. Start your service, but replace `sample` with whatever your service is called: `sudo systemctl start sample`
7. Enable your service so that it will start at server boot, again replacing `sample` as needed: `sudo systemctl enable sample`
8. Direct nginx to reverse proxy your outward facing server (with ports 80/443) to whatever port you've specified in Step 3 above. See [nginx](nginx) for an example. Save this in `/etc/nginx/sites-available/nginx`, and symlink it to `/etc/nginx/sites-enabled/nginx` with `ln -s /etc/nginx/sites-available/nginx /etc/nginx/sites-enabled`
9. Test your nginx configuration for errors with `sudo nginx -t`
10. If it's good, restart it with `sudo systemctl restart nginx`
11. And open your firewall to all these lovely, scary, risky ports with `sudo ufw allow 'Nginx Full`


## Summary

Again, I can't vouch for anyone else or there specific configuration or settings, but I'm happy to try and help as able. This worked for me on a brand new DO droplet.
