import asyncio
import tornado.web
import tornado.websocket
import os
import json
import datetime

from spirograph import Spirograph, Point

class DefaultHandler(tornado.web.RequestHandler):
    def initialize(self, graph):
        self.graph = graph
    def get(self):
        self.render("index.html")

class LiveSocket(tornado.websocket.WebSocketHandler):
    clients = set()
    def initialize(self, graph):
        self.graph = graph

    def open(self):
        print("new connection")
        LiveSocket.clients.add(self)

    def on_message(self, message):
        try:
            data = json.loads(message)
            self.sessionid = data["sessionid"]
            self.graph.add_client(data["sessionid"], data["width"], data["height"])
        except:
            print("*** got", message)

    def on_close(self):
        self.graph.remove_client(self.sessionid)
        LiveSocket.clients.remove(self)

    @classmethod
    def send_message(cls, message: str, sessionid: str):
        # print(f"Sending message {message} to {len(cls.clients)} client(s).")
        for client in cls.clients:
            if client.sessionid == sessionid:
                client.write_message(message)


class Application(tornado.web.Application):
    def __init__(self, graph):
        handlers = [
            (r"/ws", LiveSocket, dict(graph=graph)),
            (r'/favicon.ico', tornado.web.StaticFileHandler),
            (r'/static/', tornado.web.StaticFileHandler),
            (r"/.*", DefaultHandler, dict(graph=graph)),

        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "html"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)


def test_distance():
    p = Point(0,0)
    d = p.distance(1,1)
    import math
    assert(d == math.sqrt(2))

async def main():
    # test_distance()
    # return 

    loop = asyncio.get_event_loop()
    graph = Spirograph(loop, LiveSocket.send_message)

    app = Application(graph)
    app.listen(80)

    
    loop.call_later(0, graph.periodic)

    shutdown_event = asyncio.Event()
    await shutdown_event.wait()

if __name__ == "__main__":
    try:
        print("starting")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exiting")




