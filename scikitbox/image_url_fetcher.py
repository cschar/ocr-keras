
import sys,os,json,urllib2



def fetch_image_json(image_string,user_ip,url_referer,start_page=0,result_size=8,image_size="medium"):
	''' Query the google image api with an image string and return 
	the resulting json data'''

	GET_string = "%20".join(image_string.split(" "))
	url = ('https://ajax.googleapis.com/ajax/services/search/images?' + \
       'v=1.0&q='+GET_string+'&userip='+user_ip+'&start='+str(start_page)) + \
	'&rsz='+str(result_size)+'&imgsz='+image_size

	request = urllib2.Request(url, None, {'Referer': url_referer})
	response = urllib2.urlopen(request)

	# Process the JSON string.
	results = json.load(response)
	return results

def parse_images_urls(json_results):
	'''Parse the json for the image urls we want'''
	if json_results == None: return
	urls = []
	for key in json_results:
		if key == 'responseData':
			for i in range(len(json_results[key]['results'])):
				url = json_results[key]['results'][i]['url']
				#print url
				urls.append(url)

	return urls


def write_files(urls,directory="images/"):
	'''Using a list of image urls, fetch the images and write them 
	to disk. method returns number of succesfully written images'''
	#5 second tiemout
	url_timeout = 5
	count = 0
	accepted_extensions = ['.jpg','.png']
	for url in urls:
		try:
			filetype = url[-4:]
			if url[-4:] in accepted_extensions:

				name = "iuf_"+url[7:30].replace("/","") + str(count) + filetype
				url_image = urllib2.urlopen(url,timeout=url_timeout).read()
				fd = open(directory+name,'wb')
				fd.write(url_image)
				fd.close()
				count += 1
				print 'wrote to' + name
			else:
				print 'skipping' + url
		except urllib2.HTTPError as e:
			print e
		except urllib2.URLError as e2:
			print e2
	return count

def fetch_urls(search_text):
	'''fetch medium and small images for double the results'''
	fetched_img_urls = []
	for start in range(0,64,8): # max google api params
		json = fetch_image_json(search_text,"","",start_page=start,
	      result_size=8,image_size="medium")
		fetched_img_urls += parse_images_urls(json)
		json = fetch_image_json(search_text,"","",start_page=start,
	      result_size=8,image_size="small")
		fetched_img_urls += parse_images_urls(json)	
	return fetched_img_urls


def main():
	if len(sys.argv) > 1:
		image_query = " ".join(sys.argv[1:])
	else:
		image_query = 'red grapes'
	import random
	total = 0
	max_page = 64
	result_size = 8
	for start in range(0,max_page,result_size):
		print '[  ]fetching start @ %d' % start
		json = fetch_image_json(image_query,"bloomfilters","",start_page=start)
		urls = parse_images_urls(json)
		current_count = write_files(urls)
		print '[    ] retrieved %d/%d images' % (current_count,result_size)
		total += current_count

	print "\n Done: successfully retreived %d/%d image files" % (total,max_page)

if __name__ == '__main__':
	main()
