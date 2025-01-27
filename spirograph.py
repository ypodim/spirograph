import random 
import json
import math

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def distance(self, x, y):
        delta_x = x-self.x
        delta_y = y-self.y
        d = math.sqrt(delta_x*delta_x + delta_y*delta_y)
        return d
    def __str__(self):
        return "%d,%d" % (self.x, self.y)

class Circle:
    def __init__(self, center: Point, r):
        self.center = center
        self.radius = r
        self.angle = 0
    def get_point(self, p=1):
        x = p * self.radius * math.cos(self.angle)
        y = p * self.radius * math.sin(self.angle)
        return Point(x+self.center.x, y+self.center.y)

class Spirograph:
    def __init__(self, loop, send_message):
        self.loop = loop
        self.send_message = send_message
        # self.last_point = Point(1100,100)
        self.first_time = True
        self.number_of_iterations = 0
        self.c1 = Circle(Point(500,500), 205)
        self.c2 = Circle(Point(), 79)
        self.step = 0.1
        # self.angle = 0
        self.clients = {}

    def add_client(self, sessionid, w, h):
        print("adding client", sessionid, w,h)
        iterations = math.lcm(self.c1.radius, self.c2.radius)
        iterations = iterations / self.c1.radius
        print("will need iterations: ", iterations)
        self.clients[sessionid] = dict(width=w, height=h, last_point=None)
        cx=self.c1.center.x
        cy=self.c1.center.y
        r=self.c1.radius
        color="#f00"
        data = dict(type="circle",cx=cx,cy=cy,r=r,color=color)
        line = json.dumps(data)
        self.send_message(line, sessionid)

    def remove_client(self, sessionid):
        print("client left", sessionid)
        self.clients[sessionid] = None

    def is_first_iteration(self):
        if self.first_time:
            self.first_time = False
            return True
        else:
            return False
        
    def is_last_iteration(self):
        iterations = math.lcm(self.c1.radius, self.c2.radius)
        iterations = iterations / self.c1.radius
        i = self.c2.angle / (2*math.pi)

        print(int(i), iterations)

    def get_next_point(self):
        ratio = self.c1.radius / self.c2.radius
        self.c1.angle += self.step
        self.c2.angle += ratio * self.step

        self.c2.center = self.c1.get_point()

        return self.c2.get_point(p=0.5)

    def get_next_color(self):
        return "#00f"
        
    def periodic(self):
        # if self.store["actions"]:
        #     if self.store["actions"][-1] == "reset":
        #         self.first_time = True
        #         self.store["actions"].pop()

        for sessionid, config in self.clients.items():
            if config is None:
                # skip clients who didn't send window dimensions yet
                continue

            self.is_last_iteration()

            p2 = self.get_next_point()
            if config["last_point"] is None:
                p1 = p2
            else:
                p1 = config["last_point"]
            
            config["last_point"] = p2
            color = self.get_next_color()
            data = dict(type="line",x1=p1.x,y1=p1.y,x2=p2.x,y2=p2.y,color=color)
            line = json.dumps(data)
            self.send_message(line, sessionid)

        self.loop.call_later(0.01, self.periodic)




