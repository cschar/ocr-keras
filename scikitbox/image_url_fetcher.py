
import sys,os,json,shutil, requests, random

import logging


logger = logging.getLogger(__name__)


class CheapAPILimitExceededException(Exception):
	pass

def fetch_image_json(image_string, image_size="medium", start_index=1, API_KEY=None):
	''' Query the google image api with an image string and return 
	the resulting json data'''
	API_KEY = os.environ['GOOGLE_CUSTOM_SEARCH_API_KEY'] if not API_KEY else API_KEY
	image_string = "+".join(image_string.split(" "))
	url = ('https://www.googleapis.com/customsearch/v1?' +
	'q={search_query}&cx=001996507256426061711%3Azxscobp2hsm&fileType=jpg' +
	'&imgSize={image_size}&searchType=image' +
	'&start={start_index}' +
	'&key={API_KEY}').format(search_query=image_string,
	 image_size=image_size,  start_index=start_index,
	 API_KEY=API_KEY)
	

	image_json = requests.get(url).json()
	if image_json.get('error'):
	# if image_json['error']['errors'][0]['domain'] == 'usageLimits':
		raise CheapAPILimitExceededException
	return image_json

def parse_images_urls(json_results):
	'''Parse the json for the image urls we want'''
	image_links = []
	for item in json_results['items']:
		image_links.append(item['link'])

	return image_links


def write_files(urls,directory="images/"):
	'''Using a list of image urls, fetch the images and write them 
	to disk. method returns number of succesfully written images'''
	#5 second tiemout
	url_timeout = 5
	count = 0
	accepted_extensions = ['.jpg','.png']
	for url in urls:
		#clean any query string on end of name
		url = url.split('?',1)[0]
		try:
			filetype = url[-4:]
			if url[-4:] in accepted_extensions:

				file_path = directory+"iuf_"+url[7:30].replace("/","") + str(count) + filetype
				
				response = requests.get(url, stream=True)
				with open(file_path, 'wb') as out_file:
				    shutil.copyfileobj(response.raw, out_file)
				del response

				count += 1
				logger.debug('wrote to: ' + file_path)
			else:
				logger.debug('skipping {}'.format(url))
		except Exception as e:
			logger.debug(e)
	return count

def fetch_urls(search_text):
	urls = []

	for i in range(1,6):
		# for size in ['large','medium']:
		for size in ['medium']:
			json = fetch_image_json(search_text,image_size=size, start_index=i)
			urls += parse_images_urls(json)
	

	return urls


def main():
	# logger.debug = print # redirect to stdout (py3)
	if len(sys.argv) > 1:
		image_query = " ".join(sys.argv[1:])
	else:
		image_query = 'red grapes'
	total = 0
	json = fetch_image_json(image_query)
	urls = parse_images_urls(json)
	print('fetched %s' % urls)
	total = write_files(urls)

	print("\n Done: wrote %s image files" % (total))


if __name__ == '__main__':
	main()
