
import sys,os,json,urllib2, requests



def fetch_image_json(image_string, image_size="medium", API_KEY=None):
	''' Query the google image api with an image string and return 
	the resulting json data'''
	API_KEY = os.environ['API_KEY'] if not API_KEY else API_KEY
	GET_string = "+".join(image_string.split(" "))
	url = ('https://www.googleapis.com/customsearch/v1?' +
	'q={search_query}&cx=001996507256426061711%3Azxscobp2hsm&fileType=jpg' +
	'&imgSize={image_size}&searchType=image' +
	'&key={API_KEY}').format(search_query=image_string, image_size=image_size, API_KEY=API_KEY)
	
	# deprecated :(
	# url = ('https://ajax.googleapis.com/ajax/services/search/images?' + \
 #       'v=1.0&q='+GET_string+'&userip='+user_ip+'&start='+str(start_page)) + \
	# '&rsz='+str(result_size)+'&imgsz='+image_size

	response = requests.get(url)

	return response.json()

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
			if url[-4:] in accepted_extensions or cleaned_url in accepted_extensions:

				name = "iuf_"+url[7:30].replace("/","") + str(count) + filetype
				url_image = urllib2.urlopen(url,timeout=url_timeout).read()
				fd = open(directory+name,'wb')
				fd.write(url_image)
				fd.close()
				count += 1
				print 'wrote to' + name
			else:
				print 'skipping {}'.format(url)
		except urllib2.HTTPError as e:
			print e
		except urllib2.URLError as e2:
			print e2
	return count

def fetch_urls(search_text):
	'''fetch medium and small images for double the results'''
	fetched_img_urls = []

	json = fetch_image_json(search_text,image_size="medium")
	fetched_img_urls += parse_images_urls(json)


def main():
	if len(sys.argv) > 1:
		image_query = " ".join(sys.argv[1:])
	else:
		image_query = 'red grapes'
	import random
	total = 0
	
	json = fetch_image_json(image_query)
	urls = parse_images_urls(json)
	print 'fetched %s' % urls
	total = write_files(urls)

	print "\n Done: wrote %s image files" % (total)

if __name__ == '__main__':
	main()
