# Django scikit-learn test app

great chart for scikit-learn: 
http://www.datasciencecentral.com/profiles/blogs/the-making-of-a-cheatsheet-emoji-edition

Makes use of the google custom search image api to collect meak training data.
Then passes it to a SVM classifier which stupidly tries to then detect whether
the test images belong in the positive or negative images featureset camps.

deployed here for testing: https://thawing-springs-8648.herokuapp.com/


Specify custom buildpack and push to heroku
```sh
  $ heroku login
  $ heroku config:set BUILDPACK_URL=https://github.com/kennethreitz/conda-buildpack
  $ git push heroku master
  $ heroku open     # Open the app in the browser
```

### Update files in Heroku
```sh
  $ git push heroku master
```

## Develop locally
Install requirements into a virtualenv:

```sh
  $ conda create --name my_snakes_env python=3  #(or 2)
  $ source activate my_snakes_env
  $ pip install -r requirements.txt
  $ pip install -r conda-requirements.txt
  $ deactivate # Stop virtualenv when you are done
```

## Running locally

Locally:

```sh
  $ python manage.py runserver
```

Open browser at `http://0.0.0.0:8000`


## License
MIT License

