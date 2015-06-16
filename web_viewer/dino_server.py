import tornado.ioloop
import tornado.web
import os
import pandas as pd
import numpy as np

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_map.html")

class DinoFilter(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_filter.html")
		
class DinoCheckinvsDuracion(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_checkinduracion.html")

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

class checkinduracion(tornado.web.RequestHandler):
    def get(self):
        df = self.df
        # from the notebook
        checkin_data = df.loc[df["type"] == "check-in"]
        checkin_grouped = checkin_data.groupby("id")["time"].count()
        entrada_grouped = df.groupby("id")["time"].min()
        salida_grouped = df.groupby("id")["time"].max()
        entrada_grouped = pd.DataFrame(entrada_grouped)
        salida_grouped = pd.DataFrame(salida_grouped)
        checkin_grouped = pd.DataFrame(checkin_grouped)
        result = pd.concat([salida_grouped, entrada_grouped, checkin_grouped], axis=1)
        result.columns = ['horaEntrada', 'horaSalida', 'numCheckin']
        result['duracion'] = (result['horaEntrada'].dt.hour + result['horaEntrada'].dt.minute/60) - (result['horaSalida'].dt.hour + result['horaSalida'].dt.minute/60)
        result = result.drop('horaEntrada', 1)
        result = result.drop('horaSalida', 1)
        result_list = result.to_dict("registros")
        self.write({"rows" :result_list})
        
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
    df["time"] = pd.to_datetime(df.Timestamp, format="%Y-%m-%d %H:%M:%S")

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/data", DataHandler,{"df":df}),
        (r"/filter", DinoFilter),
        (r"/CheckinvsDuracion", DinoCheckinvsDuracion),
        (r"/checkin_dur", checkinduracion,{"df":df}),
        (r"/filter_data", FilterData,{"df":df}),
        (r"/static/(.*)", tornado.web.StaticFileHandler,
            {"path": settings["static_path"]})

    ], **settings)
    application.listen(8100)
    print("ready")
    tornado.ioloop.IOLoop.current().start()

