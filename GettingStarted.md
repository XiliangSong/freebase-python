freebase-python provides an easy way to acces [freebase.com](http://www.freebase.com/)'s API.

# A Simple Example #
We'll be using an example query to demonstrate aspects of freebase-python.
```
query = {
    "name" : "The Beatles",
    "type" : "/music/artist",
    "album" : []
}
```

Let's just make a simple read query for freebase:
```
>>> import freebase
>>> result = freebase.mqlread(query)
>>> print result["album"]
[u'Please Please Me', u'From Me to You', u'Introducing... The Beatles', u'She Lo...
```

We could do the same for sandbox-freebase.com:
```
>>> import freebase.sandbox
>>> result = freebase.sandbox.mqlread(query)
```

For simplicity, you can call the class freebase and perform your operation. If you want to manage different connections with different settings, it is also possible to create HTTPMetawebSessions:
```
>>> from freebase import HTTPMetawebSession
>>> fms = HTTPMetawebSession("api.freebase.com")
>>> sms = HTTPMetawebSession("api.sandbox-freebase.com")
>>> result = fms.mqlread(query)
>>> fms is not sms
True
```
This would be useful if you wanted to be able to easily switch between using sandbox-freebase.com and freebase.com or if you wanted to create many sessions to execute in parallel.

# The API #
A full list of the freebase apis is at the [metaweb\_api\_service page](http://www.freebase.com/view/freebase/metaweb_api_service). Most of them are supported here.

## mqlread / mqlwrite ##

### [mqlread](http://www.freebase.com/view/en/api_service_mqlread) ###
```
>>> r = freebase.mqlread(query, asof=None)
```
`mqlread` is used to read information from freebase. The query must be written in MQL. For more information on MQL, refer to the [MQL and Freebase API reference guide](http://mql.freebaseapps.com/). You can also test your queries on the [Query Editor](http://www.freebase.com/app/queryeditor/), which can provide additional information on the query if you're stuck. `asof` is "as-of-time."

### mqlreaditer ###
```
>>> r = freebase.mqlreaditer(query, asof=None)
```
This is `mqlread`, but it returns a python generator with the results. This way, you can construct a query that would take too long on its own and just iterate through the results.
```
>>> r = freebase.mqlreaditer({"type":"/music/artist", "name":None})
>>> r
<generator object mqlreaditer at 0x......>
>>> for i in r:
...     print i["name"] # if you have problems with outputting unicode, try, print i["name"].encode("<utf-8>")
...
Blonde Redhead
Bruce Cockburn
Buck Owens
Dwight Yoakam
Led Zeppelin
Yo La Tengo
Black Sabbath
Kings of Leon
Aphex Twin
...
```
### mqlreadmulti ###
```
r = mqlreadmulti(queries, asof=None)
```
`mqlreadmulti`, as the name suggests, is used to execute many queries.
```
>>> r = mqlreadmulti([
      {"id":"/en/the_beatles", "name":None}, 
      {"id":"/en/the_police", "name":None}
    ])
>>> for i in r:
...     print i["name"]
...
The Beatles
The Police
```
Granted, this example query could be written more succinctly like so:
```
>>> r = mqlread([{"id|=" : ["/en/the_beatles", "/en/the_police"],
                 "name" : None}])
>>> for i in r:
...     print i["name"]
The Beatles
The Police
```
But that's missing the point. The point is that you can execute multiple queries of any sort with `mqlreadmulti`.
### [mqlwrite](http://www.freebase.com/view/en/api_service_mqlwrite) ###
```
>>> r = freebase.mqlwrite(query)
```
`mqlread`'s sister, `mqlwrite` writes to freebase. It's especially important to consult the [reference guide](http://mql.freebaseapps.com/), because writes are even more complicated than reads.

## User Account ##

### [login](http://www.freebase.com/view/en/api_account_login) ###
```
>>> freebase.login(username=andrew, password=secret)
```
### [logout](http://www.freebase.com/view/en/api_account_logout) ###
```
>>> freebase.logout()
```
### [user\_info](http://www.freebase.com/view/guid/9202a8c04000641f800000000c36a842) ###
```
>>> freebase.login(username, password)
>>> print freebase.user_info()
{ u'status': u'200 OK',
  u'username': u'nitromaster101',
  u'code': u'/api/status/ok',
  u'name': u'Andrew Rodriguez', 
  u'guid': u'#9202a8c04000641f80000000095397d1', 
  u'id': u'/user/nitromaster101', 
  u'transaction_id': u'cache;...' }
>>> freebase.logout()
>>> print freebase.user_info()
Traceback (most recent call last):
...
MetawebError: request failed ...
```
Returns a typical dictionary response with information on the user.
### [loggedin](http://www.freebase.com/view/en/api_account_loggedin) ###
```
>>> freebase.logout()
>>> amiloggedin = freebase.loggedin()
>>> if amiloggedin:
        print freebase.user_info()
>>> else: print "User not logged in."
User not logged in.
```
Returns a boolean indicating whether or not a user is logged in or not.

## Private Domains ##

### [create\_private\_domain](http://www.freebase.com/edit/topic/en/api_service_create_private_domain) ###
```
>>> r = freebase.sandbox.create_private_domain(domain_key, display_name)
```
This creates a private domain for you to use. It's not a base, but it's close.
```
>>> freebase.sandbox.login(username="andrew", password="secret")
>>> freebase.sandbox.create_private_domain("hello", "Hello, world!")
{ u'status': u'200 OK',
  u'domain_key': u'hello', 
  u'code': u'/api/status/ok', 
  u'domain_id': u'/guid/9202a8c04000641f800000000c8320c6', 
  u'transaction_id': u'cache;...' }
```


### [delete\_private\_domain](http://www.freebase.com/edit/topic/en/api_service_delete_private_domain) ###
```
>>> r = freebase.sandbox.delete_private_domain(domain_key)
```
This deletes an **empty** private domain.
```
>>> freebase.sandbox.login(username="andrew", password="secret")
>>> freebase.sandbox.delete_private_domain("hello")
{ u'status': u'200 OK',
  u'code': u'/api/status/ok', 
  u'domain_id': u'/user/nitromaster101/hello', 
  u'domain_name': u'Hello, world!',
  u'transaction_id': u'cache;...' }
```


## trans ##

### [trans raw](http://www.freebase.com/view/en/api_trans_raw) ###
```
>>> r = freebase.raw(id)
```
Given the id of a document, `raw` will return that blob exactly as it is. Note that you cannot ask for the raw of a topic because it is not a document. First, you have to isolate what document you want and then you can get its content.
```
>>> query = {
        "id" : "/en/the_beatles",
        "/common/topic/article" : {"id" : None, "optional" : True, "limit" : 1}
    }
>>> r = freebase.mqlread(query)
>>> article_id = r["/common/topic/article"]["id"]
>>> freebase.raw(article_id)
"The Beatles were a rock and pop band from Liverpool, England that formed in 1960...
```

You can actually do `raw` on any document content: an article, image, pdf, etc. For an image, you would do something like this:
```
>>> query = {
        "id" : "/en/the_beatles",
        "/common/topic/image" : {"id" : None, "optional" : True, "limit" : 1}
    }
>>> r = freebase.mqlread(query)
>>> image_id = r["/common/topic/image"]["id"]
>>> im = freebase.raw(image_id) # Now you have the actual image.
```
The image's URL would be `api.freebase.com/api/trans/raw/{image_id}`.

### [trans blurb](http://www.freebase.com/view/en/api_trans_blurb) ###
```
r = freebase.blurb(id, break_paragraphs=False, maxlength=200)
```
The major difference between `blurb` and `raw` is that `blurb` only returns text (no html) and can only be done on certain objects (articles, other pieces of text), while `raw` can return anything, but can't be called on topics. `maxlength` is the number of characters that should be displayed and must be larger than the sum of the number of characters in the first word plus 3 (for '...').
```
>>> query = {
        "id" : "/en/the_beatles",
        "/common/topic/article" : {"id" : None, "optional" : True, "limit" : 1}
    }
>>> r = freebase.mqlread(query)
>>> article_id = r["/common/topic/article"]["id"]
>>> freebase.blurb(article_id, maxlength=53)
"The Beatles were a rock and pop band from..."
```

### [image\_thumb](http://www.freebase.com/view/en/api_trans_image_thumb) ###
```
>>> r = freebase.image_thumb(id, maxwidth=None, maxheight=None, mode="fit", onfail=None)
```
`image_thumb` returns an image scaled around according to the arguments passed to it. The exact way the arguments are detailed is located [here](http://www.freebase.com/view/en/api_trans_image_thumb).

## Upload ##

### [upload](http://www.freebase.com/view/en/api_service_upload) ###
```
>>> r = freebase.sandbox.upload(body, content_type, document_id=False, permission_of=False)
```
`upload` uploads your string `body` to freebase. The response tells you whether or not the upload was successful and the new id of the blob you uploaded. You can connect your newly uploaded blob to a document by using the document\_id property.
```
>>> freebase.sandbox.login(username="andrew", password="secret")
>>> r = freebase.sandbox.upload("Hello, world!", "text/plain")
>>> r
{ u'/type/content/blob_id': u'315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3', 
 u'/type/content/language': u'/lang/en', 
 u'/type/content/text_encoding': u'utf-8', 
 u'/type/content/length': 13, 
 u'/type/content/media_type': u'text/plain', 
 u'type': u'/type/content', 
 u'id': u'/guid/9202a8c04000641f800000000c6f1389' }
>>> freebase.sandbox.raw(r["id"])
"Hello, world!"

```
### [uri\_submit](http://www.freebase.com/view/en/api_service_uri_submit) ###
```
>>> r = freebase.uri_submit(URI, document_id=None, content_type=None)
```
Similar to `upload`, `uri_submit` takes the URI of the information you want to upload to freebase and uploads it. You can upload any type of document and can attach it to a real document with the use of the document\_id property.
```
>>> r = freebase.sandbox.uri_submit("http://api.freebase.com")
>>> r
{ u'/type/content/blob_id': u'1a287e9f3e87b65fd629c86feea0ccb71c6de563b70662f12d3f9d45a0b41e3d', 
  u'/type/content/language': u'/lang/en', 
  u'/type/content/text_encoding': u'UTF-8', 
  u'/type/content/length': 42647, 
  u'/type/content/media_type': u'text/html',
  u'type': u'/type/content',
  u'id': u'/guid/9202a8c04000641f800000000c6f1aa5' }
```

## Random, Static-ky Services on Freebase ##

### [version](http://www.freebase.com/view/en/api_version) ###
```
>>> print freebase.version()
{ u'me': u'me/dev/135/pyroot:76103', 
  u'index': u'relevance/dev/27:74629', 
  u'code': u'/api/status/ok', 
  u'cdb': u'cdb/dev/18:72726', 
  u'graph': u'gd/dev/50:76020', 
  u'server': u'www.freebase.com', 
  u'client': u'client/dev/93:76143', 
  u'status': u'200 OK', 
  u'transaction_id': u'cache;...' }
```
Not usually needed, but it returns the current version of each of freebase's major systems.
### [status](http://www.freebase.com/view/en/api_status) ###
```
>>> print freebase.status()
{ u'status': u'200 OK',
  u'code': u'/api/status/ok',
  u'graph': u'OK',
  u'blob': u'OK', 
  u'relevance': u'OK',
  u'transaction_id': u'cache;...' }
```
Hopefully there won't be a problem, but just in case you want to check, this gives the current status of the freebase systems.