import os
import json
import tornado.web
import tornado.ioloop
import tornado.options
import extraction

tornado.options.define('port', default=8000)
entity = extraction.Extraction()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('chatbot.html')


class MsgHandler(tornado.web.RequestHandler):
    def post(self):

        if self.request.headers.get("Content-Type").startswith("application/json"):
            data = json.loads(self.request.body)

            message = data["text"]
            info = entity.extraction(message)
            self.write(info)
        else:
            self.write_error(404)


if __name__ == '__main__':
    app = tornado.web.Application(
        [
            (r'/', IndexHandler),
            (r'/chatbot', MsgHandler),
        ],
        template_path=os.path.join(os.getcwd(), 'templates'),
        # static_path=os.path.join(os.path.dirname(__file__), 'static'),
    )
    app.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.current().start()
