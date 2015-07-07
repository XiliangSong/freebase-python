# freebase-python: The Basics #

In your python program, just say:
```
import freebase
results = freebase.mqlread(query)
```

There are many api calls for your choosing. You can get information on all of them by going to [the freebase api service page](http://www.freebase.com/view/freebase/metaweb_api_service) or the GettingStarted page on this wiki. Some popular calls are `search`, `mqlread`, and `mqlwrite`.

## freebase.sandbox ##

Using `freebase.func()` issues the api call to freebase.com. You can also make queries on sandbox.freebase.com, a sandbox that's cleared every Monday. The syntax is almost identical:
```
import freebase.sandbox
results = freebase.sandbox.mqlread(query)
```

## HTTPMetawebSession ##

In case you want to keep track of the session objects that make the api calls, you can access the HTTPMetawebSession.
```
from freebase import HTTPMetawebSession, MetawebError
mss = HTTPMetawebSession("http://api.freebase.com")
results = mss.mqlread(query)
```
One advantage to using HTTPMetawebSession is that you can easily switch from connecting to freebase and connecting to sandbox. You could test your program on sandbox, make sure it all works, and then easily switch it over to freebase by just changing the HTTPMetawebSession("http://sandbox.freebase.com") to HTTPMetawebSession("http://www.freebase.com").

Another advantage is that if you could produce many HTTPMetawebSessions, and preform parallel queries... but that's usually not necessary.

# A more complicated example #

```
import freebase
query = {
  "id" : "/en/the_beatles",
  "type" : "/music/artist",
  "album" : [{
    "name" : None,
    "release_date" : None,
    "track" : {
      "return" : "count"
    }
    "sort" : "release_date"
  }]
}
results = freebase.mqlread(query)
for album in results.album:
    print album.name + " has " + album.track + " tracks"
```

As you can see, this is really just the basic example with a more complicated query. For more information on forming queries, see the [MQL Reference Guide](http://mql.freebaseapps.com/). In this case, we're looking the The Beatles and getting all their albums. With each album, we get its `name`, `release_date`, and `track`. But with `track`, we don't list the available tracks, instead we count the number of tracks present. We also sort the albums that are returned by their `release_date`.