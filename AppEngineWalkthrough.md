# Introduction #

Google AppEngine is a way to write applications that take advantage of Google's massive resources. For a basic overview you can check out their [What Is Google App Engine? page](http://code.google.com/appengine/docs/whatisgoogleappengine.html).

This walkthrough will go through the process of creating an app that uses the freebase-python library. The final product can be found at http://freebase-images.appspot.com. This walkthrough assumes that the person reading this is slightly familiar with what Google App Engine does, has some knowledge of HTML/CSS, and knows what freebase is.


# Step 1 #

We begin by setting up our development environment. Before we do anything too interesting, we have to setup the basics in our app. App Engine's own documentation does a fine job, so we'll refer to that.

First, [download the local App Engine development kit](http://code.google.com/appengine/docs/python/gettingstarted/devenvironment.html)
Next, complete the first two documentation pages: [Hello, world!](http://code.google.com/appengine/docs/python/gettingstarted/helloworld.html) and [Using the webapp Framework](http://code.google.com/appengine/docs/python/gettingstarted/usingwebapp.html). When you're done with that, come back here and we'll start making an interesting application.

# Step 2 #

The goal of the our sample application is to make an image browser for freebase. So, given a starting topic, we want all the images that have something to do with it to be shown and then the user can traverse the graph of related images. So, the first question is how do I get all the images for a given topic, say, /en/the\_beatles? The [query editor](http://freebase.com/app/queryeditor) is our friend here.

Let's start with the id,
```
[{
  "id" : "/en/the_beatles"
}]
```
Good, we see it exists. Now it we get all the properties of The Beatles,
```
[{
  "id" : "/en/the_beatles",
  "*" : [{}]
}]
```
If we look through every property, we don't see any images, or even image-related data. You can imagine that even if we did something like,
```
[{
	"id": "/en/the_beatles",
  "type" : "/music/artist",
  "*":  [{}]
}]
```
Although we get more information about The Beatle's tracks and music labels, still no images.
It turns out that The Beatles are also typed /common/topic,
```
[{
  "id":   "/en/the_beatles",
  "type": "/common/topic",
  "*":    null	
}]
```
and voila! We see there are two images: The Beatles in Millings suits and The Beatles in 1964: John Lennon, Paul McCartney, George Harrison, Ringo Starr. Now we want more information about these images.
```
[{
  "id":   "/en/the_beatles",
  "type": "/common/topic",
  "image": [{}]
}]
```
But actually, we really just want the ids.
```
[{
  "id":   "/en/the_beatles",
  "type": "/common/topic",
  "image": [{
    "id": null
  }]
}]
```
So our result should look something like,
```
"code": "/api/status/ok",
"result": [{
  "id": "/en/the_beatles",
  "image": [{
    "id": "/wikipedia/images/en_id/851535"
  },
  {
    "id": "/wikipedia/images/commons_id/4473823"
  }],
"type": "/common/topic"
}],
"status":        "200 OK",
"transaction_id": "cache;..."
```
Good.

This is getting closer to our goal, but still not ideal. We want all the images related to a certain topic, not just images about that topic. So, for /en/the\_beatles, I want images of the albums and the members of the band.

The naïve approach would be to iterate through all the properties of an object and get their images. Luckily, freebase provides a convenient way of querying everything that has to do with an object. It relies on `/type/reflect/any_master`, `/type/reflect/any_reverse`, and `/type/reflect/any_value`. `any_master` returns anything that the object points to, `any_reverse` is anything that points to the object, and `any_value` is any value related to the object. You can test the output of any of these properties in the query editor,
```
[{
  "id": "/en/the_beatles",
	"/type/reflect/any_master": [{}]
}]
```
As we can see, there are a lot of things that /en/the\_beatles point to. For one, a permission, that makes sense. Then a /common/document, which is the description. Third, /film/actor, because The Beatles were actors... This looks good, but we want images.
```
[{
  "id": "/en/the_beatles",
  "/type/reflect/any_master": [{
	  "/common/topic/image": [{
	    "id": null
    }]
  }]
}]
```
Now, we also want to include `any_reverse` for things pointing to the object. So our final query will look something like:
```
[{
  "id": "/en/the_beatles",
  "/type/reflect/any_master": [{
    "/common/topic/image": [{
      "id": null
    }]
  }],
  "/type/reflect/any_reverse": [{
    "/common/topic/image": [{
      "id": null
    }]
  }]
}]
```
We have one more caveat. If there is an object that has an `any_master` or an `any_reverse` that doesn't have an image, this query won't return anything. To get around this, we must include a few `optionals` so that an object with no images doesn't trip anything up.
```
[{
  "id": "/en/the_beatles",
  "/type/reflect/any_master": [{
    "/common/topic/image": [{
      "id": null
    }],
    "optional": true
  }],
  "/type/reflect/any_reverse": [{
    "/common/topic/image": [{
      "id": null
    }],
    "optional": true
  }]
}]
```
And that, my friends, is the final query! Woah. All that work in order to get all the images related to a topic. But surprisingly, that's a lot of the work. The rest of the application will be getting information from this query and displaying it in a friendly fashion.

# Step 3 #
**to be added**
The general idea, though, is to use the results of this query and generate a simple user interface to return images given a topic id.