
from PIL import Image, ImageFilter
from sklearn import svm
from numpy import array
from scipy import ndimage
import numpy as np
from glob import glob
import unittest,os,time
# from skimage import feature
from urllib import request as urllib2

import scikitbox.db

def get_rgb_feature_list(pil_image):
    '''ignore alpha channel if present'''
    if pil_image.mode == 'L':
        #L == grayscale
        return list(pil_image.getdata())
    else:
        ret = []
        for rgb_tuple in list(pil_image.getdata()):
            if len(rgb_tuple) == 4:
                ret.extend(rgb_tuple[0:3])
            else:
                ret.extend(rgb_tuple)
        return ret

def collect_images(filepath):
    extensions = ['jpg', 'JPG', 'png', 'PNG']
    images = []
    for ext in extensions:
        images += glob(filepath+"*."+ext)

    return images

def clean_image_dir(directory):
    priors = collect_images(directory)
    cleans = 0
    for img in priors:
        try:
            os.remove(img)
            cleans += 1
        except OSError:
            pass
    return cleans


def get_feature_list_from_directory(filepath,attach_names=False):
    image_paths = collect_images(filepath)
    features = []
    for path in image_paths:
        img = Image.open(path)
        img_features = get_rgb_feature_list(img)
        if attach_names:
            features.append((img_features,path))
        else:
            features.append(img_features)
        img.close()
    return features


def image_resize(filepath,size,destination_filepath=None):
    if destination_filepath == None:
        destination_filepath = filepath
    try:
        im = Image.open(filepath)
        im = im.resize(size)
        im.save(destination_filepath)
    except IOError as e:
        print("can't open %s, deleting" % filepath)
        os.remove(filepath)
        return 1
    return 0

def color_to_grayscale(filepath,destination_filepath=None):
    if destination_filepath == None:
        destination_filepath = filepath
    try:
        im = Image.open(filepath)
        im = im.convert("L")
        im.save(destination_filepath)
    except IOError as e:
        print("can't open %s, deleting" % filepath)
        os.remove(filepath)
        return 1
    return 0

def resize_directory(filepath,size):
    imgs = collect_images(filepath)
    deletes = 0
    for im in imgs:
        deletes += image_resize(im,size)
    print("resized %d images in %s with %d IOError deletions" % \
        ((len(imgs)-deletes),filepath,deletes))

def color_to_grayscale_directory(filepath):
    img_paths = collect_images(filepath)
    deletes = 0
    for img_path in img_paths:
        deletes += color_to_grayscale(img_path)
    print("converted %d images from rgb to grayscale in %s with %d \
    IOError deletions" %((len(img_paths)-deletes),filepath,deletes))

def normalize_directory(filepath, size):
    resize_directory(filepath,size)
    color_to_grayscale_directory(filepath)
    converted_paths = edge_detect_directory(filepath)
    return converted_paths

# def grayscale_to_edge_detection(image_filepath):
# 	from skimage import data,io,filter
# 	img = Image.open(image_filepath)
# 	size = img.size
# 	img_array = np.array(img.getdata())
# 	img_array = np.resize(img_array,size)
# 	img_array = img_array.astype(np.uint8)
# 	edges = filter.sobel(img_array)
# 	io.imsave(image_filepath+"_edge.jpg",edges)

def write_edge_detect(image_filepath,destination_filepath=None):
    if destination_filepath == None:
        destination_filepath = image_filepath
    img = Image.open(image_filepath)
    img = img.filter(ImageFilter.FIND_EDGES)
    img = img.filter(ImageFilter.SMOOTH)
    img.save(destination_filepath)
    img.close()

def edge_detect_directory(filepath):
    img_paths = collect_images(filepath)
    for img in img_paths:
        write_edge_detect(img)
    print("converted %d images from grayscale to edge detection in %s" % \
        ((len(img_paths)),filepath))
    return img_paths

def save_images_to_db(image_dir,image_type):
    mongo = db.get_bot()
    image_paths = collect_images(image_dir)
    saves = 0
    print('[ ] saving to mongodb ')
    for image_path in image_paths:
        saves += mongo.save_image(image_path,image_type)
        print('.',)
    print('\nsaved %d images to database' % saves)

def load_images_from_db(image_type,destination_directory):
    mongo = db.get_bot()
    results = mongo.get_imagetypes(image_type)
    try:
        os.makedirs(destination_directory)
    except OSError: #directory exists
        pass
    os.path.dirname(destination_directory)
    for res in results:
        try:
            path = os.path.join(destination_directory,res['filename'])
            fil = open(path,'wb')
            fil.write(res['binary'])
            fil.close()
        except IOError as e:
            print(e)
    print('loaded %d results from db' % len(results))


def train_classifier(pos_dir,neg_dir):
    start = time.time()
    print("[ ] Beginning to train svm classifier.")
    pfeatures = get_feature_list_from_directory(pos_dir)
    current_time = time.time() - start
    print("[ ] Done setting up postives (samples: %d, feautures: %d). Time: %d" \
        % (len(pfeatures), len(pfeatures[0]), current_time))
    nfeatures = get_feature_list_from_directory(neg_dir)
    current_time = time.time() - start
    print("[ ] Done setting up negatives (samples: %d, features: %d). Time: %d" \
         % (len(nfeatures), len(nfeatures[0]), current_time))

    X = pfeatures + nfeatures
    y = ["positive"]*len(pfeatures) + ["negative"]*len(nfeatures)
    print("[ ] Training with (samplesize,featuresize):(%d , %d )" %\
            (len(pfeatures)+len(nfeatures), len(pfeatures[0])))

    clf = svm.SVC(kernel='linear',C=100, cache_size=1000)
    clf.fit(X, y)
    current_time = time.time() - start
    print("[ ] Done training in: %d seconds" % (current_time))
    return clf

def test_classifier_on_single(clf,filepath): # returns (class,distance)
    img = Image.open(filepath)
    print(len(img.getdata()))
    features = get_rgb_feature_list(img)
    img.close()
    prediction = clf.predict(features)
    distance_to_hyperplane = clf.decision_function(features)
    return (prediction,distance_to_hyperplane)


