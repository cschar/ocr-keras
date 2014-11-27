# Django scikit-learn app for svm module


A django app running on heroku that provides a simple interface
for a user to collect image training data, and upload images to 
test against that training data.

## Deploy to Heroku
Clone and add to git
```sh
  $ git clone git@github.com:cclay/django-scikit-app.git
  $ git init
  $ git add .
  $ git commit -m "init"
```
Specify custom buildpack and push to heroku
```sh
  $ heroku login
  $ heroku config:set BUILDPACK_URL=https://github.com/dbrgn/heroku-buildpack-python-sklearn/
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
  $ virtualenv env
  $ source env/bin/activate
  $ pip install -r requirements.txt
  $ deactivate # Stop virtualenv when you are done
```

## Running locally

Locally:

```sh
  $ python app.py      # Use default 8080 port
```

Open browser at `http://0.0.0.0:8080`


## License
MIT License