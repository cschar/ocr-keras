import base64
from datetime import datetime
import os
import logging
from glob import glob
from multiprocessing import Process

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

try:
    import scikitbox.image_url_fetcher as iuf
    import scikitbox.trainertools as tt
except:
    import image_url_fetcher as iuf
    import trainertools as tt
    
from django.views import View


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


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('index')

class Login(View):

    def get(self, request):
        return render(request,'scikitbox/login.html')

    def post(self, request):
        logger.info("attempted to login w/ {}".format(request.POST))
        user = authenticate(username=request.POST['username'],
                            password=request.POST['password'])

        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request,'scikitbox/login.html')



@login_required
@never_cache
def index(request):
    '''index of the app giving a dashboard overview of available
    options to user'''

    test_images = static_url_collect(TEST_DIR)
    pos_images = static_url_collect(POS_DIR)
    neg_images = static_url_collect(NEG_DIR)
    # template_dict = defaultdict(None)
    template_dict = {'test_images':test_images,
                     'pos_image_count':len(pos_images),
                     'neg_image_count':len(neg_images),
                     }
    return render(request,'scikitbox/main.html', template_dict)

@login_required
def uploadSingle(request):
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
        tt.normalize_directory(NTEST_DIR, (28, 28))

        return redirect('index')

@login_required
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

@login_required
@require_http_methods(['POST'])
def setupTraining(request):
    #TODO: normalize at this step in case user forgets to after
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

@login_required
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

@login_required
def invert(request):
    img_type = request.GET['type']
    base_dir = './scikitbox/static/images/training/' + img_type
    img_paths = tt.collect_images(base_dir)

    for img_path in img_paths:
        tt.write_threshold_mask(img_path)
    return redirect('index')

@login_required
def normalizeTraining(request):
    size = (28,28)
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

@login_required
def match(request):
    match_type = request.GET['type']
    training_base = './scikitbox/static/images/training/'
    pos_dir = training_base +'pos/'
    neg_dir = training_base +'neg/'
    testnorm_dir = "./scikitbox/static/images/test_normalized/"

    if match_type == 'test':
        dir = testnorm_dir
    elif match_type == 'pos':
        dir = pos_dir
    else:
        dir = neg_dir


    test_images = tt.collect_images(dir)
    clf_results = []
    for img_path in test_images:
        try:
            result = tt.test_mlp_mnist_classifier_on_single(img_path)
            clf_results.append(result)
        except ValueError as e:
            logger.debug(img_path + "   " + str(e))

    img_urls = static_url_collect(dir)
    image_clf_results = []

    for i in range(len(img_urls)):
        image_clf_results.append(
                {"test_url":img_urls[i],
                "data":clf_results[i],
                 "bleb": "blebb",
                })

    return render(request,'scikitbox/match.html',
                  { 'image_clf_results' : image_clf_results })


@login_required
@csrf_exempt
def save_image(request):
    format, imgstr = request.POST['imgBase64'].split(';base64,')
    ext = format.split('/')[-1]
    data = base64.b64decode(imgstr)

    file_name = 'upload{}.{}'.format(datetime.now().isoformat(), ext)
    file_path = TEST_DIR + file_name
    with open(file_path, 'wb') as f:
        f.write(data)

    # TODO use media folder and Model.FileUpload
    all_urls = static_url_collect(TEST_DIR)
    file_url = [x for x in all_urls if file_name in x][0]

    ntest_path = os.path.join(NTEST_DIR, file_name)
    with open(ntest_path,"wb") as norm_fil:
        norm_fil.write(data)
    tt.normalize_directory(NTEST_DIR, (28, 28))

    return JsonResponse(data={'url': str(file_url)})