# Two examples tornado projects
## First is a simple Tornado Server project
## Second is a simple Tornado WebSocket project

# 1.An introduction for simple Tornado 
The `etc` folder is nginx and supervisorctl configuration.
The `nginx.conf` is for nginx configuration. 
```
/etc/nginx.conf
```
The `tornado.conf` is for supervisorctl process management.
```
/etc/supervisor/tornado.conf
```

You can launch tornado server by the `main.py` file. Its content as shown:
```
import tornado.ioloop
import tornado.web
import os

from tornado.options import define, options
define("port", default=8100, help="run on the given port", type=int)

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        # The `index.html` is located in `templates` folder
        self.render("index.html")

def make_app():
    settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
    )
    return tornado.web.Application(
        [(r"/", MainHandler)], 
        **settings
    )

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
```
So, use the command `python main.py` to browse, open http://localhost:8100 in the addree bar in the browser.

<br/>
<br/>

# 2.An introduction for simple Tornado WebSocket
The `etc` folder is nginx and `supervisorctl` configuration.
The `nginx.conf` is for `nginx` configuration. 
```
/etc/nginx.conf
```
The `ws.example.com.conf` is for the site in nginx configuration. 
```
/etc/nginx/vhost/ws.example.com.conf
```
The `WebSocketProject.conf` is for `supervisorctl` process management.
```
/etc/supervisor/WebSocketProject.conf
```
Since this configuration file is for WebSocket, so there is a little difference in `nginx` file.
In `nginx.conf`, a more sophisticated example in which a value of the “Connection” header field in a request to the proxied server depends on the presence of the “Upgrade” field in the client request header:
```
http {
    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }
```
The hop-by-hop headers including “Upgrade” and “Connection” are not passed from a client to proxied server, therefore in order for the proxied server to know about the client’s intention to switch a protocol to WebSocket, these headers have to be passed explicitly:
```
    server {
        ...

        location /chatsocket {
            proxy_pass http://localhost:9090;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Origin '';
            proxy_read_timeout 300s;
        }
    }
```
Nginx WebSocket Proxying Explanation: https://nginx.org/en/docs/http/websocket.html

<br/>
<br/>

# Attention Please:
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


<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
