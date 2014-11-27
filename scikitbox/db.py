import pymongo,bson,os



class MongoBot():
	def __init__(self,db_name,db_user,db_pass):
		self.client = pymongo.MongoClient(
			"mongodb://"+db_user+":"+db_pass+"@dogen.mongohq.com/"+\
			db_name, 10036)
		print 'mongobot client created'
		self.db = self.client[db_name]
		self.images = self.db.images

	def save_image(self,image_filepath,image_type):
		saved = 0
		try:
			img_file = open(image_filepath,"rb")
			binary_data = bson.Binary(img_file.read())
			img_file.close()
			
			self.images.insert({
				"type": image_type,
				"directory": os.path.dirname(image_filepath),
				"filename": os.path.basename(image_filepath),
				"binary": binary_data
				})
		except IOError as e:
			print e
			return saved

		saved = 1
		return saved

	def get_imagetypes(self,image_type):
		results = []
		for image in self.images.find({"type":image_type}):
			results.append(image)

		return results


def get_bot():
	db_name = os.environ["MONGO_NAME"]
	user = os.environ["MONGO_USER"]
	password = os.environ["MONGO_PASS"]
	mongo = MongoBot(db_name,user,password)
	return mongo


if __name__ == "__main__":
	db_name = os.environ["MONGO_NAME"]
	user = os.environ["MONGO_USER"]
	password = os.environ["MONGO_PASS"]
	mb = MongoBot(db_name,user,password)

	mb.save_image("./images/spinning_cylinders.jpg","positive_car")
	for i in mb.get_imagetypes("positive_car"):
		print i["_id"]
	

