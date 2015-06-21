import tornado.ioloop
import tornado.web
import os
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
import math
import random
import datetime 
import time
sns.set_style("darkgrid")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_map.html")

class DinoUser(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_user.html")

class DinoFilter(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_filter.html")

class FilterData(tornado.web.RequestHandler):
    def get(self):
        x_min = float(self.get_argument("x_min"))
        x_max = float(self.get_argument("x_max"))
        y_min = float(self.get_argument("y_min"))
        y_max = float(self.get_argument("y_max"))
        t_min = np.datetime64(int(self.get_argument("t_min")),"ms")
        t_max = np.datetime64(int(self.get_argument("t_max")),"ms")

        df = self.df
        area = (df["X"]<=x_max) & (df["X"]>=x_min) & (df["Y"]<=y_max) & (df["Y"]>=y_min)
        time = (df["time"] >= t_min) & (df["time"] <= t_max)
        # as int
        guests = sorted(df.loc[area & time,"id"].unique().tolist())
        self.write({"guests" : guests})

    def initialize(self, df):
        self.df = df


class DataHandler(tornado.web.RequestHandler):
    def get(self):
        df = self.df
        guest_id = self.get_argument("id", None)
        if guest_id is None:
            guest_id = np.random.choice(df["id"])
        else:
            guest_id = int(guest_id)
        guest_df = df.loc[df["id"]==guest_id]
        guest_df_list = guest_df.to_dict("records")        
        self.write({"array" :guest_df_list})

    def initialize(self, df):
        self.df = df[["X","Y","id","Timestamp","type"]]

class DistanceHandler(tornado.web.RequestHandler):

    def obtainTotalDistanceByUser(self,guest_df):
        i = 1
        velocity_list = []
        guest_matrix = guest_df.values
        total_distance = 0
        d = 0
        v = 0
        t = 0
        
        while i < len(guest_df):

            # Distance math...

            xi = int(guest_matrix[i-1][3])
            yi = int(guest_matrix[i-1][4])

            xf = int(guest_matrix[i][3])
            yf = int(guest_matrix[i][4])

            d = math.sqrt(pow((xf-xi),2)+pow((yf-yi),2))
            total_distance += d

            # Time math

            ti = datetime.datetime.strptime(guest_matrix[i-1][0], '%Y-%m-%d %H:%M:%S')
            tf = datetime.datetime.strptime(guest_matrix[i][0], '%Y-%m-%d %H:%M:%S')
            
            t = (tf-ti).total_seconds()
            
            # Velocity math
            v = d/t
        
            velocity_list.append(v)
            i += 1
        return total_distance
        
    def get(self):
        df = self.df
        guest_id = self.get_argument("id", None)
        guest_id = int(guest_id)

        guest_df = df.loc[df["id"]==guest_id]
        response = self.obtainTotalDistanceByUser(guest_df)
        self.write({"response" :response})

    def initialize(self, df):
        self.df = df

class FilterByCheckin(tornado.web.RequestHandler):
    def get(self):
        num = int(self.get_argument("num"))
        df = self.df
        # From the notebook
        checkin_filter = df['type'] == 'check-in'
        checkin_df = df[checkin_filter]
        groupUserCheckin = checkin_df['id'].value_counts()
        
        checkInFiltered = groupUserCheckin[groupUserCheckin < num]
        checkin_df = pd.DataFrame(checkInFiltered, columns=['number'])
        self.write({"checkins" :checkin_df.to_dict()})
    def initialize(self, df):
        self.df = df

settings = {"template_path" : os.path.dirname(__file__),
            "static_path" : os.path.join(os.path.dirname(__file__),"static"),
            "debug" : True
            } 

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "C:/MC1 2015 Data/park-movement-Fri.csv")
    print('loading...')
    df = pd.read_csv(path)
    # df = df.loc[df["id"]==103006] #temp...
    print('converting time...')
    df["time"] = pd.to_datetime(df.Timestamp, format="%Y-%m-%d %H:%M:%S")

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/data", DataHandler,{"df":df}),
        (r"/filter", DinoFilter),
        (r"/filter_data", FilterData,{"df":df}),
        (r"/static/(.*)", tornado.web.StaticFileHandler,
            {"path": settings["static_path"]}),
        (r"/dinoUser", DinoUser),
        (r"/checkins", FilterByCheckin,{"df":df}),
        (r"/distance", DistanceHandler,{"df":df}),

    ], **settings)
    application.listen(8100)
    print("ready")
    tornado.ioloop.IOLoop.current().start()

