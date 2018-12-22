# tornado_testsite

A simple example on telling you how to config a tornado webapp project on CentOS. 

Including /etc/nginx.conf, /etc/supervisor/tornado.conf

Attention Please:
If you restarted your cloud server, and the webapp failed to autostart, and then, you want to confirm that what's wrong with that? You entered the command 
```
supervisorctl status
```
and it gave that error message, like this "unix:///tmp/supervisor.sock refused connection", 
so after searching google, the solution is 
```
sudo supervisord -c /etc/supervisord.conf   

sudo supervisorctl status  # see is it running well?

sudo service nginx restart # restart your nginx
```

https://stackoverflow.com/questions/20067116/supervisorctl-error-unix-var-run-supervisord-sock-refused-connection

