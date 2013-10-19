django-bootstrap
================

Django + Bootstrap + Angular.js. A great way to kickstart your next app. Coming soon.

Features
========

DjAjax
------
* Easily add AJAX functionalities to your Django app.
* Seamless validation of AJAX params using Django forms.
* Designed to be lightweight.
* Inspired by Dajaxice but this is ultra-lightweight and has built-in
  form validation.

DjBase
------
* Custom JSON encoder that encodes `datetime`'s in ISO format. Supports
  arbitrary objects that has a `to_json` method.

* Parses ISO formatted datetime's easily.  

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

External Dependencies
=====================
External dependency refer to external module.


| App  | Dependencies
|------|-------------
`djbase`        | `dateutil`


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
from djajax.core import djajax_autodiscover
djajax_autodiscover()

urlpatterns = patterns('',
    # ... your URLs ...

    # You're free to use any prefix but ajax is recommended
    url(r'^ajax/', include('djajax.urls')),
)
```

To register a regular method as an AJAX method:
```python
from djajax.decorators import djajax

@djajax(method='POST')
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

