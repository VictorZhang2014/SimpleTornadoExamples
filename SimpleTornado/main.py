import tornado.ioloop
import tornado.web
import os

from tornado.options import define, options
define("port", default=8100, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):

    def get(self):
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