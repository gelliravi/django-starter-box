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
* Deploy static files to Amazon S3.
* Serve static and dynamic files over Amazon Cloudfront.
* Auto-minify and gzip CSS and JavaScript files. 
* Auto-compress PNG and JPEG images.
* Auto-versioning of static files so that expiry dates can be set to max
  on Cloudfront.
* Rewrite URLs in CSS.

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

| Name   | Version  | Tested only with 
|--------|----------|-----------------
Python   | >= 2.7   | 2.7.3
Django   | >= 1.5.1 | 1.5.1
sqlite   | whatever Django supports | -

**Python 3 Compatibility**: We try to make it Python 3 compat as much as possible,
although I might have missed something out. Feel free to open issues on this.

External Dependencies
=====================
External dependency refer to external module.

You might be able to use a lower version. Just run the tests to see if they work.

| App           | Dependencies| Tested only with
|---------------|-------------|-----------------
`djbase`        | `dateutil`  |
`djaccount`     | [`facebook-sdk`](https://github.com/pythonforfacebook/facebook-sdk) (python) | 0.4.0
`djcdn`         | [`django-storages`](http://code.larlet.fr/django-storages/) and its dependencies    | 1.1.8
                | `boto` (AWS Python SDK) |  2.9.7
                | [`cssmin`](https://github.com/zacharyvoase/cssmin)  | 0.2.0
                | [`slimit`](https://github.com/rspivak/slimit.git)   | 0.8.0
                | `jpegoptim` (only if you're compressing JPEG files) |
                | `pngcrush` (only if you're compressing PNG files)   |


Internal Dependencies
=====================
Internal dependency refers to internal modules within this project.

| App           | Dependencies
|---------------|-------------
`djajax`        | `djbase`
`djaccount`     | `djbase`
`djcdn`         | `djbase`

DjAjax
======
For extensive examples, refer to `djajax/tests/ajax.py`.

Setting up
-----------
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

How to use
----------
You would require `JSON.stringify` if your JavaScript framework
does not have an equivalent function.

Include the following somewhere to load JSON2 which is a polyfill
for `JSON.stringify` and `JSON.parse`.
```html
<script src="//cdnjs.cloudflare.com/ajax/libs/json2/20121008/json2.min.js"></script>
```

```javascript
// Using jQuery:
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
Put the following base settings in `settings.py`.
They will enable media and static files to be uploaded and served from S3.
If you are serving static files directly from S3,
you need to **ensure your S3 bucket is public by default**, so that you
don't have to explicitly make every file public. Google
on how to do this. If you're serving from CloudFront, we're not sure
whether you need to do so. Experiment around.

```python
INSTALLED_APPS = (
    'django.contrib.staticfiles',   # You must use Django's staticfiles
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

`StaticStorage` will minify, gzip CSS and JavaScript files by default (customizable),
and upload the resulting files to S3.  Minified files will have file names
such as `xxx.min.css` or `xxx.min.js`. Gzipped versions are stored separately 
from the minified versions and will have file names such as `xxx.min.gz.css`. 
The file extension is preserved to enable correct MIME type detection.

 It will also crush/compress PNG and JPEG images. The file names will be unchanged.

If you want to serve static files from your servers, and have CloudFront
distribute them, override the base settings with:

```python
# Remove STATICFILES_STORAGE from above to use Django's default filesystem storage.

# collectstatic will put all collected files here. 
# Remember to config your web server to serve static files from here as well.
STATIC_ROOT         = '<path>/static/'  # Local file system path

# Map your static CloudFront to <your-domain>.com
STATIC_URL          = '//<id>.cloudfront.net/static/'
```

### Separate production and development settings

For rapid development, you wouldn't want to have to keep pushing static
files to S3 every time you make a change. For development, we
recommend serving static files from local web servers (could be Django's runserver).
Usually, on development, you directly serve static files from a specified 
directory so that you don't even need to do `collectstatic`.

```python
# Remove STATICFILES_STORAGE from above to use Django's filesystem storage.

# Directly serve static files from filesystem.
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '<path>/<to>/static',
)

# Everything else can be the same except for *_URL which will point to
# local server.
STATIC_URL  = STATIC_ROOT

# For media files, you could use S3 (development version or not)
# or the filesystem.
# MEDIA_URL   = MEDIA_ROOT
```

Auto-versioning of static files
-------------------------------
This section is for production environment only, 
as there is no point in versioning static files for development.

Here are the steps for deploying versioned static files to S3 and 
optionally serving over CloudFront.

### Setting up

1. Sign up for S3 and CloudFront accounts. Map your CloudFront distribution
   to your S3 bucket.  

2. Install and configure `djcdn` as per above, but use `VersionedStaticStorage` so
   `collectstatic` can upload all files to S3 with version info.

   ```python
   STATICFILES_STORAGE = 'djcdn.storage.s3.VersionedStaticStorage'

   # Optionally, use CloudFront.
   # Remember to map your CloudFront distribution to your S3 bucket domain.
   STATIC_URL = '//<id>.cloudfront.net/%s' % CDN_STATIC_S3_PATH
   ```

3. Use the `cdn` template tag instead of `static`. 
   For example, `{% cdn 'css/main.css'  %}`
   will output something like "//xxx.cloudfront.net/static/20131023-2334d/css/main.min.gz.css". The tag will use `request` to auto-detect whether the browser supports gzip.

   For media files, use `{% cdn 'photos/1.jpg' type='DEFAULT' %}`. 
   Note that DEFAULT is case-sensitive.

### Workflow 

1. Download static files to your production server(s).

2. Run `./manage.py collectstatic` as usual on your web server. If you have multiple
   load-balanced web servers, just choose any one with the static files.

3. Do a `./manage.py cdn_done` to mark the current version as completely uploaded.
   If there is an error, DO NOT perform `cdn_done`. You should simply retry step 2.

4. **Not implemented yet** Clean up old versions in S3 by doing `./manage.py cdn_clean`. 
   It will keep the 3 most recent versions, in case clients still use old versions of your web pages when they don't refresh.

5. Restart your Django apps to reload new version info. 
   Generated HTML will then point to the new version of static files.

6. Optional step: warm up the Cloudfront cache files by visiting your website.
   Or you could use an automated tool to do so. This will cause Cloudfront
   to fetch the static files from your S3 bucket.

### How it works

`djcdn` uses path versioning as
the method of appending a query string doesn't seem to work on certain HTTP
proxies. The entire static files directory is simply treated as a new version
even if only some files have changed since the last version. This is for 
simplicity. Versioning at the individual file level is too much work and complicated.
Furthermore, you can clean up by simply discarding entire versioned directories.
This shouldn't be a problem if your static files are at most several MBs big.
(Storage is cheap.)

1.  Django's `collectstatic` command will use `VersionedStaticStorage` to 
    minify, compress and gzip static files using your favorite tools such 
    as `pngcrush` and then upload the resulting files to S3. 

2. `VersionedStaticStorage` differs from `StaticStorage` in that it will 
    add a version string to the path.

    It generates a unique version number such as
    `20131023-a4b5686` based on the current date. 

    For example, a minified and gzipped CSS file will be at 
    "s3.amazonaws.com/{your-bucket}/static/{version}/css/main.min.gz.css"   

    To keep track of the new version, it inserts a `CDNVersion` object 
    into the database (marked as not done initially).
  
3.  Once the upload is complete and error-free, use `cdn_done` to mark
    the version as complete. This is needed as there is no way to know 
    when `collectstatic` is done, other than to wrap `collectstatic` in a command.
    In the future, we could implement a wrapper for `collectstatic` that 
    auto-marks the upload as complete.

4.  The `cdn` template tag gets the latest version info on app startup. 
    It detects from the `HTTP_ACCEPT_ENCODING` header
    whether the browser supports gzip encoding, and output the right path
    accordingly.

Does DjCDN work with Django-compressor?
---------------------------------------

Yes, because `django-compressor` works independently of `djcdn`.
Good thing is that `compressor` also auto-versions each file it generates
independently of how `djcdn` does it.

You'd need to configure `compressor` to use CloudFront (or any other CDN).
See http://stackoverflow.com/questions/8688815/django-compressor-how-to-write-to-s3-read-from-cloudfront

What features are not supported (yet)?
--------------------------------------

1. Have CloudFront fetch versioned files from your servers instead of S3.
   To allow this, you'd need to run the compression and versioning process
   on every web server that serves static files, as there is no guarantee
   which will be hit by the CloudFront servers.
   Due to this reason, this feature is currently not supported.
   One workaround is to copy the versioned files and distribute
   to the rest of the web servers.

   If your servers are all connected to a common storage (networked disks),
   then you'd have to ensure the static files are stored there. And then you
   could modify the code to store the files on the common storage.
   
2. Compiling SASS, LESS, CoffeeScript and etc. files. 

3. File-level versioning. This would involve crawling the entire static
   file directory to version each file and store the version info in a database/cache
   for lookup by the `cdn` template tag. Cleaning up old version would be slightly
   more troublesome.
   We don't see the need for this unless
   your static files are more than 10 MB?

Optional settings
-----------------
The following `djcdn` specific settings are used by `DefaultStorage`, `StaticStorage` 
and `VersionedStaticStorage`.

```python
# Files types that will have gzip applied for static files.
CDN_STATIC_COMPRESSED_TYPES     = ('css', 'js')  # Lowercase

# Same but for media files
CDN_DEFAULT_COMPRESSED_TYPES    = ()

# List of filters to apply for each file type (lowercase)
CDN_STATIC_FILTERS              = {
    'css'   : ('filters.cssmin', 'filters.csspath'),
    'js'    : ('filters.slimit',),
    'png'   : ('filters.pngcrush',),  # Remove if you don't want to compress PNG
    'jpg'   : ('filters.jpegoptim',), # Remove if you don't want to compress JPEG
    'jpeg'  : ('filters.jpegoptim',),
}

# Same but for media files.
CDN_DEFAULT_FILTERS              = {
    # none
}

# Expiry age for static files. Will affect the HTTP headers stored in S3.
# This will set the Cache-Control max-age. 
# The Expires header will be calculated relative to current date and time.
CDN_STATIC_EXPIRY_AGE      = 3600 * 24 * 365 # seconds

CDN_DEFAULT_EXPIRY_AGE     = 3600 * 24 * 365 # seconds    
```

`filter.csspath` rewrites `url(...)` and `@import ...`. It works
by replacing `STATIC_ROOT` at the front of the URL with `STATIC_URL`. 
For example, `/static/img/icon.png` is rewritten to `//{id}.cloudfront.net/static/20131023-133acbde/img/icon.png`.

Note that if you want your files to never expire, for example, media files
that are never replaced or versioned static files, it seems there is no way to have 
a relative on-the-fly Expires header on S3. S3 just doesn't calculate Expires
on-the-fly.

There are a few ways to fix this for S3:

1. Run a cron job to update the Expires header
   for the entire bucket once a year or so. 

2. Set `CDN_*_EXPIRY_AGE` to a large value.

3.  Use CloudFront and map it to your S3 bucket. 
    Then you can set a large TTL (Time-to-live) value.

The third option is the easiest and safest, although that will cost 
a little amount of money.

More info on [`django-storage` S3 settings](http://django-storages.readthedocs.org/en/latest/backends/amazon-S3.html).
