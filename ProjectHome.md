**IMPORTANT NOTE**

The freebase-python library uses the legacy, deprecated, Freebase APIs. For instructions on the new Freebase APIs, see here: https://developers.google.com/freebase/

---

Freebase.com has an open API that can be used to access and update structured data.
The RESTful http-based API is completely documented at [Freebase.com](http://www.freebase.com/view/freebase/api) along with some simple examples. This library provides a python interface to that API.

Usage should be as simple as:
```
>>> import freebase
>>> freebase.mqlread({"id": "/en/david_bowie", "name": None})
{u'id': u'/en/david_bowie', u'name': u'David Bowie'}
```

For more information, see GettingStarted.

This library also provides a number of command-line utilities and APIs for creating, dumping, and reloading schema to make it easy to programatically create schema and move schema from sandbox-freebase.com to freebase.com. For more on this see the [recipes](http://code.google.com/p/freebase-python/w/list?q=label:Recipe) pages.

Discussion of this project is hosted at [Freebase developers mailing list](http://lists.freebase.com/mailman/listinfo/developers).

Installing is easy, if you have easy\_install, just say
```
$ easy_install freebase
```

freebase-python will use the [jsonlib2](http://code.google.com/p/jsonlib2) library if it is already installed, and otherwise will fall back to using the `json` (Python 2.6+) or `simplejson` (Python 2.5 and below) modules.

If you don't have easy\_install, you can get it by running http://peak.telecommunity.com/dist/ez_setup.py