import os
import logging
from glob import glob
from multiprocessing import Process

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

import scikitbox.image_url_fetcher as iuf
import scikitbox.trainertools as tt

logger = logging.getLogger(__name__)
TEST_DIR = "./scikitbox/static/images/test/"
NTEST_DIR = "./scikitbox/static/images/test_normalized/"
POS_DIR = "./scikitbox/static/images/training/pos/"
NEG_DIR = "./scikitbox/static/images/training/neg/"


def static_url_collect(directory_path):
    '''helper method to get static url paths of images located inside
    the directory_path parameter'''
    extensions = ['jpg', 'JPG', 'png', 'PNG']
    images = []
    for ext in extensions:
        images += glob(directory_path+"*."+ext)

    images = ["../"+(image.split("./scikitbox/")[1]) for image in images]
    return images


def index(request):
    '''index of the app giving a dashboard overview of available
    options to user'''

    logger.error('hey')
    test_images = static_url_collect(TEST_DIR)
    pos_images = static_url_collect(POS_DIR)
    neg_images = static_url_collect(NEG_DIR)
    # template_dict = defaultdict(None)
    template_dict = {'test_images':test_images,
                     'pos_image_count':len(pos_images),
                     'neg_image_count':len(neg_images),
                     'alert_message': None}
    return render(request,'scikitbox/main.html', template_dict)




def uploadSingle(request):
    '''receives an uploaded image from user and save it to the
    test folder, aswell as normalizing it to a test_normalized folder'''
    if request.method == "POST":
        uploaded_image = request.FILES['upload']
        name = uploaded_image.name

        test_path = os.path.join(TEST_DIR,name)
        fil = open(test_path,"wb")
        data = uploaded_image.read()
        fil.write(data)
        fil.close()

        ntest_path = os.path.join(NTEST_DIR,name)
        norm_fil = open(ntest_path,"wb")
        norm_fil.write(data)
        norm_fil.close()
        tt.normalize_directory(NTEST_DIR, (100, 100))

        response = HttpResponse("file uploaded successfully")
        response.__setitem__("content-type","text/text")
        return response

def clear(request,folder_target):
    ''' clears any .jpgs or .pngs in the folder_target directory'''
    if folder_target == 'Test':
        removed = tt.clean_image_dir(TEST_DIR)
        tt.clean_image_dir(NTEST_DIR)
    elif folder_target == 'Positive':
        removed = tt.clean_image_dir(POS_DIR)
    elif folder_target == 'Negative':
        removed = tt.clean_image_dir(NEG_DIR)
    else:
        return Http404
    logger.debug("removed %s images from %s", removed, folder_target)
    return redirect(reverse('index'))

@require_http_methods(['POST'])
def setupTraining(request):
    ''' uses google image api to fill up either a positive or negative
    training folder with samples for later use in the svm classifier'''
    classifier = request.POST['classifier']
    search_text = request.POST.get('training_keywords', 'red grapes')  # default search query

    try:
        fetched_img_urls = iuf.fetch_urls(search_text)
    except iuf.CheapAPILimitExceededException:
        return HttpResponse("API limit exceeded for today")

    save_path = "./scikitbox/static/images/training/"
    if classifier == "positive":
        save_path += "pos/"
    elif classifier == "negative":
        save_path += "neg/"
    p = Process(target=iuf.write_files,
                args=(fetched_img_urls,save_path))
    p.start()

    template_dict = {'type':classifier,
                    'count': len(fetched_img_urls),
                    'images':fetched_img_urls}
    return render(request,'scikitbox/search_results.html', template_dict)

@never_cache
def viewTraining(request,classifier_type): #positive or negative
    '''displays the current images in the training folder corresponding
to the classifier_type parameter'''
    if classifier_type == "Positive":
        training_images = static_url_collect("./scikitbox/static/images/training/pos/")
    elif classifier_type == "Negative":
        training_images = static_url_collect("./scikitbox/static/images/training/neg/")
    else:
        raise Http404

    template_dict = {'images': training_images,
                     'type' : classifier_type,
                     'count': len(training_images)}

    return render(request, 'scikitbox/view_images.html', template_dict)

def normalizeTraining(request):
    '''normalizes the images inside the training folders by the following:
     resizing them to a size of 100x100, converting them to grayscale, and
     then applying an edge detection filter to make it easier for the
     svm to pick out useable pixel featuers'''

    size = (100,100)
    base_dir = './scikitbox/static/images/training/'

    tt.normalize_directory(base_dir + 'pos/', size)
    tt.normalize_directory(base_dir + 'neg/', size)
    # tt.normalize_directory()
    pos_convert_paths = static_url_collect(base_dir + 'pos/')
    neg_convert_paths = static_url_collect(base_dir + 'neg/')

    return render(request, 'scikitbox/view_images.html',
                  {'images': pos_convert_paths + neg_convert_paths,
                   'type' : 'normalized images',
                   'count': '{} pos, {}'.format(len(pos_convert_paths),
                                                len(neg_convert_paths))})


def matchTestGallery(request):
    '''trains a svm classifier using the image data stored in the
    training folders. With the classifier, it inputs all the normalized
    user images as test data. The resulting matches are classified
    either as "postive" or "negative" and a resulting distance to the
    classifier divider or 'hyperplane' is appended for each user image
    test.'''
    training_base = './scikitbox/static/images/training/'
    pos_dir = training_base +'pos/'
    neg_dir = training_base +'neg/'
    clf = tt.train_classifier(pos_dir,neg_dir)
    testnorm_dir = "./scikitbox/static/images/test_normalized/"
    test_dir = "./scikitbox/static/images/test/"

    test_images = tt.collect_images(testnorm_dir)
    clf_results = [] #("positive",np.array)
    for image in test_images:
        try:
            result = tt.test_classifier_on_single(clf,image)
            clf_results.append(result)
        except ValueError as e:
            logger.debug(image + "   " + str(e))

    #Get static paths
    normalized_test_urls = static_url_collect(testnorm_dir)
    test_urls = static_url_collect(test_dir)
    image_clf_results = []

    for i in range(len(normalized_test_urls)):
        image_clf_results.append({"test_url":test_urls[i],
                            "normalized_url":normalized_test_urls[i],
                            "clf_result":clf_results[i][0],
                            "clf_distance":clf_results[i][1]})


    template_dict = { 'image_clf_results' : image_clf_results }
    return render(request,'scikitbox/match.html', template_dict)

