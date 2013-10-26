django-bootstrap
================

Django + Bootstrap + Angular.js. A great way to kickstart your next app. Coming soon.

Goals
-----
* Capture the best practices for developing and deploying a modern, scalable
  web app, with support for CDN.
* Provides many tools to quickly prototype/build your apps.

Why create this?
-----------------------
* Django itself is great, but I found many things missing when
  I started building my first Django app.
* I built many sites, and I want to consolidate the common stuff into 
  a single framework for better maintenance.

Features
========

DjAccount
---------
* Supports Facebook connect. Support for other services coming soon.
* Supports many basic account operations such as password reset, verifying email and etc.


DjAjax
------
* Easily add AJAX functionalities to your Django app.
* Seamless validation of AJAX params using Django forms.
* Designed to be lightweight: no dependencies on other JavaScript frameworks.
* Inspired by Dajaxice but this is ultra-lightweight and has built-in
  param validation support.

DjBase
------
* Custom JSON encoder that encodes `datetime`'s in ISO format. Supports
  arbitrary objects that has a `to_json` method.

* Parses ISO formatted datetime's easily.  

* Useful model fields: `ISODateTimeField`, `FixedCharField`, `PickleField`

DjCDN
-----
* Deploy dynamic media and user-uploaded files to Amazon S3.
* Serve static and dynamic files over Amazon Cloudfront.
* Auto-versioning of static files so that expiry dates can be set to max
  on Cloudfront.

Installation
============
You can create a fork of this project or download individual apps within 
here and plug into existing projects.

Please also take note of the dependencies of the app you want to install.


Requirements
============
This is what we think are the sufficient requirements even though we have only 
tested with those versions listed.

Please feel free to try whether they work with other versions. 
You can do a `git clone` followed by a `./manage.py test` to quickly test
whether the apps work with your versions. You also need SQLite and its Python connector
if you want to do a `./manage.py test`.

| Name | Version  | Tested only with 
|------|----------|-----------------
Python   | >= 2.7   | 2.7.3
Django   | >= 1.5.1 | 1.5.1
sqlite   | whatever Django supports | -

**Python 3 Compatibility**: We try to make it Python 3 compat as much as possible,
although I might have missed something out. Feel free to open issues on this.

External Dependencies
=====================
External dependency refer to external module.


| App  | Dependencies
|------|-------------
`djbase`        | `dateutil`
`djaccount`     | [`facebook-sdk`](https://github.com/pythonforfacebook/facebook-sdk) (python) >= 0.4.0
`djcdn`         | [`django-storages`](http://code.larlet.fr/django-storages/) and its dependencies,  Amazon `boto` (AWS Python SDK)


Internal Dependencies
=====================
Internal dependency refers to internal modules within this project.

| App  | Dependencies
|------|-------------
`djajax`        | `djbase`
`djaccount`     | `djbase`

DjAjax
======
For extensive examples, refer to `djajax/tests/ajax.py`.

To install, modify `<project>/settings.py` and add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = (
    # ... other apps ...

    # add the lines
    'djajax',
    'djbase',
)
```

No configuration required!

To auto-discover AJAX methods, add the following to your main `<project>/urls.py`:
```python
from djajax.core import ajax_autodiscover
ajax_autodiscover()

urlpatterns = patterns('',
    # ... your URLs ...

    # You're free to use any prefix but ajax is recommended
    url(r'^ajax/', include('djajax.urls')),
)
```

To register a regular method as an AJAX method:
```python
from djajax.decorators import ajax

@ajax(method='POST')
def createAccount(request, name, email, password):
    # ... do something ...

    if email_taken:
        raise Exception('Email is taken')

    return {'id': user_id}
```

To use in JavaScript:
```javascript
// jQuery:
// JSON.stringify requires polyfill... see json.org
$.ajax({
  url: "/ajax/createAccount",{
    type: 'POST',
    headers: {
        // read more about CSRF : https://docs.djangoproject.com/en/1.5/ref/contrib/csrf/
        'X-CSRFToken': '...'
    },
    data: {data: JSON.stringify({name: 'John', email: 'john@john.com', password: '123'})}
  }
})
.done(function( data ) {
    if (data.error)
    {
        // TODO: handle error.
        // available fields:
        // data.error.message: Message of Exception thrown in AJAX method.
        // data.error.type:    Class name of Exception thrown in AJAX method.
        // data.error.data:    Extra error details.
    }

    alert(data.id);
})
.fail(function() {
    alert( "error" );
});
```

DjCDN
=====

Required settings
-----------------
Put the following in `settings.py`:

```python
INSTALLED_APPS = (
    ...,
    'djcdn',
    'djbase',
    ....
)

# djcdn settings
CDN_STATIC_S3_PATH      = "static/" # You may change this. Ends with slash
CDN_DEFAULT_S3_PATH     = "media/"  # You may change this. Ends with slash

# Django-storage settings
AWS_ACCESS_KEY_ID       = {{ your key id here }}
AWS_SECRET_ACCESS_KEY   = {{ your secret key here }}
AWS_STORAGE_BUCKET_NAME = {{ your bucket name here }}

# Django settings to put both static and media files in S3
DEFAULT_FILE_STORAGE    = 'djcdn.storage.s3.DefaultStorage'
STATICFILES_STORAGE     = 'djcdn.storage.s3.StaticStorage'

MEDIA_ROOT          = '/%s' % CDN_DEFAULT_S3_PATH
MEDIA_URL           = '//s3.amazonaws.com/%s/%s' % (AWS_STORAGE_BUCKET_NAME, CDN_DEFAULT_S3_PATH)
STATIC_ROOT         = "/%s" % CDN_STATIC_S3_PATH
STATIC_URL          = '//s3.amazonaws.com/%s/%s' % (AWS_STORAGE_BUCKET_NAME, CDN_STATIC_S3_PATH)
ADMIN_MEDIA_PREFIX  = STATIC_URL + 'admin/'
```

If you're using CloudFront, there is no real need to upload your static files 
to S3. You could use these settings instead, to have your servers
serve static files and have CloudFront distribute them.

```python
# Remove STATICFILES_STORAGE from above to use Django's default.

# Map your media CloudFront to <bucket-name>.s3.amazonaws.com
MEDIA_URL           = '//<id>.cloudfront.net/%s' % CDN_DEFAULT_S3_PATH

STATIC_ROOT         = '<path>/static/'  # Local file system path

# Map your static CloudFront to <your-domain>.com
STATIC_URL          = '//<id>.cloudfront.net/static/'
```

More info on [`django-storage` S3 settings](http://django-storages.readthedocs.org/en/latest/backends/amazon-S3.html).

Optional settings
-----------------

```python
from datetime import datetime, timedelta

# use this to get an expiry of 1 year
def _get_aws_headers():
    # locale independent... the GMT format should just be pure numbers.
    days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
              'Sep', 'Oct', 'Nov', 'Dec')

    age = 3600 * 24 * 365  # 1 year in secs 

    now = datetime.utcnow()
    expires = now + timedelta(seconds=age)
    expires_str = expires.strftime('%%s, %d %%s %Y %H:%M:%S GMT')
    expires_str = expires_str % (days[expires.weekday()], months[expires.month-1])
    headers = {
        'Expires'       : expires_str,
        'Cache-Control' : 'max-age=%s' % age, 
    }

    return headers

AWS_HEADERS = _get_aws_headers()
```

Note that if you want your files to never expire, for example, media files
that are never replaced once uploaded, it seems there is no way to have 
a relative Expires header (or at least have AWS calculate the
Expires header on the fly). You may want to try using only Cache-control
 and leave out the absolute Expires header.
 Another approach is to run a cron job to update the Expires header
 for the entire bucket once a year or so. 

Auto-versioning of static files
-------------------------------
### Setting up

1. Sign up for S3 and CloudFront accounts. Map your CloudFront distribution
   to your S3 bucket.

2. Install and configure `djcdn`.

3. Use the `cdn` template tag instead of `staticfile`. 
   For example, `{% cdn 'css/main.css' %}`
   will output something like "//xxx.cloudfront.net/static/20131023-2334d/css/main.min.gz.css". The tag will auto-detect whether the browser supports gzip.

## Workflow 
Here's the workflow for deploying versioned static files to S3 and serving
over CloudFront:

1. Download static files to your production server(s).

2. Run `./manage.py cdn_deploy` on your web server. If you have multiple
   load-balanced web servers, just choose any one will do.

3. `cdn_deploy` will first collect and then upload static files to your 
   S3 bucket in `CDN_STATIC_S3_PATH`. 
   It will minify and gzip CSS and JavaScript files. Gzipped versions will be 
   stored as separate copies to support browsers that do not have gzip capability. 
   It will also crush/compress images.

   Path will have an added version number.
   For example, a minified and gzipped CSS file will be at 
   "s3.amazonaws.com/<your-bucket>/static/<version>/css/main.min.gz.css"


4. Clean up old versions in S3 and the local disk by doing `./manage.py cdn_clean`. 
   Only the 3 most
   recent versions will be kept. (Just in case clients still use old versions
   if they don't refresh your web pages.)

5. Restart your Django apps to reload new version info. 
   Generated HTML will then point to the new version of static files.

6. Optional step: warm up the Cloudfront cache files by visiting your website.
   Or you could use an automated tool to do so. This will cause Cloudfront
   to fetch the static files from your S3 bucket.

### How it works

1. Your entire static files directory will be built first
    using the Django's `collectstatic` commmand. `cdn_deploy` will then 
    minify, compress and gzip using your favorite tools such as `pngcrush` 
    and then upload the resulting files to S3. 

2. It generates a unique version number such as
    `20131023-a4b5686` based on the current date. It uses path versioning as
    the method of appending a query string doesn't seem to work on certain HTTP
    proxies. The entire static files directory is simply treated as a new version
    even if only some files have changed since the last version. This is for 
    simplicity. Versioning at the individual file level is too much work and complicated.
    Furthermore, you can clean up by simply discarding entire versioned directories.
    This shouldn't be a problem if your static files are at most several MBs big.
    (Storage is cheap.)

3. The `cdn` template tag detects from the `HTTP_ACCEPT_ENCODING` header
   whether the browser supports gzip encoding, and output the right path
   accordingly.

### Does it work with Django-compressor?
   Yes, because `django-compressor` works independently of `djcdn`.
   Good thing is that `compressor` also auto-versions each file it generates
   independently of how `djcdn` does it.
   
   You'd need to configure `compressor` to use CloudFront (or any other CDN).
   See http://stackoverflow.com/questions/8688815/django-compressor-how-to-write-to-s3-read-from-cloudfront

### What features are not supported (yet)?

1. Have CloudFront fetch versioned files from your servers instead of S3.
   To allow this, you'd need to run the compression and versioning process
   on every web server that serves static files, as there is no guarantee
   which will be hit by the CloudFront servers.
   Due to this reason, this feature is currently not supported.
   One workaround is to copy the versioned files and distribute
   to the rest of the web servers.

   If your servers are all connected to a common storage (networked disks),
   then you'd have to ensure the static files are stored there. And then you
   could modify the code to skip uploading to S3.
   

2. Compiling SASS, LESS, CoffeeScript and etc. files. 

3. File-level versioning. This would involve crawling the entire static
   file directory to version each file and store the version info in a database/cache
   for lookup by the `cdn` template tag. Cleaning up old version would be slightly
   more troublesome.
   We don't see the need for this unless
   your static files are more than 10 MB?


