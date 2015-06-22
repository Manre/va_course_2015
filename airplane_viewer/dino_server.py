import tornado.ioloop
import tornado.web
import os
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import random
import math
import datetime 
import time
import json
sns.set_style("darkgrid")

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("home.html")

class CrashHandler(tornado.web.RequestHandler):
	def get(self):
		results = int(self.get_argument("results"))
		
		groupby_year = df.Year.value_counts()
		year_df = pd.DataFrame(groupby_year, columns=['count'])
		sorted_year = year_df.sort(['count'], ascending=[False]).head(results)
		
		self.write({"data" : sorted_year.to_dict() })

	def initialize(self, df):
		self.df = df

class FatalitiesHandler(tornado.web.RequestHandler):
	def get(self):
		results = int(self.get_argument("results"))
		
		group_year_agg_fatalities = df.groupby(['Year']).agg('sum')['Fatalities']
		fatalities_df = pd.DataFrame(group_year_agg_fatalities)
		sorted_most_fatalities = fatalities_df.sort(['Fatalities'], ascending=[False]).head(results)
		
		self.write({"data" : sorted_most_fatalities.to_dict() })

	def initialize(self, df):
		self.df = df

class YearVsFatalitiesHandler(tornado.web.RequestHandler):
	def get(self):
		
		group_year_agg_fatalities = df.groupby(['Year']).agg('sum')['Fatalities'].astype('int')
		fatalities_df = pd.DataFrame(group_year_agg_fatalities)
		result = pd.concat([fatalities_df], axis=1, join='inner' )
		
		self.write(json.loads(result.to_json(orient='split')))

	def initialize(self, df):
		self.df = df

class CrashByDecadeHandler(tornado.web.RequestHandler):
	def floor_decade(self, date_value):
		return (date_value.year // 10) * 10

	def get(self):
		
		ts = df.set_index(['Date'])
		temp = ts.groupby(self.floor_decade).count()['Fatalities']
		
		self.write({"data" : temp.to_dict() })

	def initialize(self, df):
		self.df = df

class WorstAirlinesHandler(tornado.web.RequestHandler):
	def get(self):

		results = int(self.get_argument("results"))
		
		groupby_operator = df.Operator.value_counts()
		operator_df = pd.DataFrame(groupby_operator, columns=['count'])
		top_10_worst_operator = operator_df.sort(['count'], ascending=[False]).head(results)
		
		self.write({"data" : top_10_worst_operator.to_dict()})

	def initialize(self, df):
		self.df = df

class WorstAirplanesHandler(tornado.web.RequestHandler):
	def get(self):

		results = int(self.get_argument("results"))
		
		groupby_type = df.Type.value_counts()
		type_df = pd.DataFrame(groupby_type, columns=['count'])
		top_10_worst_type = type_df.sort(['count'], ascending=[False]).head(results)
		
		self.write({"data" : top_10_worst_type.to_dict()})

	def initialize(self, df):
		self.df = df

class TimeHandler(tornado.web.RequestHandler):
	def get(self):

		start_hour = str(self.get_argument("start")) #format: hh:mm
		end_hour = str(self.get_argument("end"))	#format: hh:mm	

		temp_df = df
		# Time cleaning...
		temp_df['Time'] = df['Time'].map(lambda x: str(x).lstrip('c: '))
		# Creating the time zones...
		custom_time = temp_df[(temp_df.Time > start_hour) & (temp_df.Time < end_hour)].shape
		
		data = {'data' : custom_time[0]}
		custom_df = pd.DataFrame(pd.Series(data), columns=['Crashes'])
		
		self.write({"data" : custom_df.to_dict()})

	def initialize(self, df):
		self.df = df

settings = {"template_path" : os.path.dirname(__file__),
			"static_path" : os.path.join(os.path.dirname(__file__),"static"),
			"debug" : True
			} 

if __name__ == "__main__":
	path = os.path.join(os.path.dirname(__file__), "../../documentation/data/Airplane_Crashes_and_Fatalities_Since_1908.csv")
	print('loading...')
	df = pd.read_csv(path)
	print('Removing columns...')
	df = df.drop('Registration', 1)
	df = df.drop('Summary', 1)
	df = df.drop('Flight #', 1)
	df = df.drop('cn/In', 1)
	print('Playing with Date & Time...')
	#Convert to Panda format
	df['Date'] = pd.to_datetime(df.Date)
	df['Time'] = pd.to_datetime(df.Time)
	#Creating Year column
	df['Year'] = df['Date'].map(lambda x: x.year)
	print('Cleaning the data...')
	df['Fatalities'] = df['Fatalities'].fillna(0)
	df['Time'] = df['Time'].fillna(0)
	df['Operator'] = df['Operator'].fillna('Unknown')
	df['Type'] = df['Type'].fillna('Unknown')

	application = tornado.web.Application([
		(r"/", MainHandler),
		(r"/crashes/years", CrashHandler,{"df":df}),
		(r"/fatalities/years", FatalitiesHandler,{"df":df}),
		(r"/YearVsFatalities", YearVsFatalitiesHandler,{"df":df}),
		(r"/crashes/decade", CrashByDecadeHandler,{"df":df}),
		(r"/worst/airlines", WorstAirlinesHandler,{"df":df}),
		(r"/worst/airplanes", WorstAirplanesHandler,{"df":df}),
		(r"/crashes/hours", TimeHandler,{"df":df}),
		(r"/static/(.*)", tornado.web.StaticFileHandler,
			{"path": settings["static_path"]})

	], **settings)
	application.listen(8100)
	print("ready")
	tornado.ioloop.IOLoop.current().start()

