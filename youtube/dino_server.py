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

class CategoriesHandler(tornado.web.RequestHandler):
	def findCategoryFrom(self,video):
		tmp = df[df['name'] == video]
		return 'Video not found' if tmp.empty else tmp.values[0][3]

	def get(self):
		
		for category in categories:
			matrix_videos = df[df['category'] == category].values
			for video in matrix_videos:
				video_name = video[0]
				for i in range(9,29):
					related_video = str(video[i])
					related_video_category = self.findCategoryFrom(related_video)
					if related_video_category != 'Video not found':
						categories[category][related_video_category] += 1

		self.write(categories)

	def initialize(self, df):
		self.df = df


settings = {"template_path" : os.path.dirname(__file__),
			"static_path" : os.path.join(os.path.dirname(__file__),"static"),
			"debug" : True
			} 

if __name__ == "__main__":
	path = os.path.join(os.path.dirname(__file__), "../../documentation/data/youtube/0.txt")
	print('loading...')
	df = pd.read_csv(path, sep="\t", header=None)
	df.columns = ['name', 'uploader', 'age', 'category', 'length', 'views', 'rate', 'group', 'comments', 'related_video 1', 'related_video 2', 'related_video 3', 'related_video 4', 'related_video 5', 'related_video 6', 'related_video 7', 'related_video 8', 'related_video 9', 'related_video 10', 'related_video 11', 'related_video 12', 'related_video 13', 'related_video 14', 'related_video 15', 'related_video 16', 'related_video 17', 'related_video 18', 'related_video 19', 'related_video 20']
	print('Cleaning the data...')
	df['age'] = df['age'].fillna(0)
	df['views'] = df['views'].fillna(0)
	df['rate'] = df['rate'].fillna(0)
	df['category'] = df['category'].fillna('Unknown')
	df['length'] = df['length'].fillna(0)
	print('Creating the categories dictionary...')
	categories = df['category'].value_counts().index.values
	tmp = {}
	for i in range(len(categories)):
		tmp[categories[i]] = {'id': i}
	categories = tmp
	print('Second part...')
	for c in categories:
		tmp = categories[c]
		for c2 in categories:
			tmp[c2] = 0
	

	application = tornado.web.Application([
		(r"/", MainHandler),
		(r"/categories", CategoriesHandler,{"df":df}),
		(r"/static/(.*)", tornado.web.StaticFileHandler,
			{"path": settings["static_path"]})

	], **settings)
	application.listen(8100)
	print("ready")
	tornado.ioloop.IOLoop.current().start()

