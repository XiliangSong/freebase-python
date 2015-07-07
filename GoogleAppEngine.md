# Introduction #

Adding 3rd party libraries to Google AppEngine can be tricky, but don't worry, adding support for freebase-python is a breeze! For a working example of an application on AppEngine, you can see the application at http://freebase-images.appspot.com and the code is [in the repository](http://code.google.com/p/freebase-python/source/browse/#svn/trunk/examples/freebase-images-appengine)


# Details #

In order to use the python freebase api in your Google AppEngine project, just issue the following command in the project's folder:
```
svn checkout http://freebase-python.googlecode.com/svn/trunk/freebase freebase
```
This will only install the actual code that runs the library, not all the egg business that usually comes with it.

And that's it. No need to `easy_install` or `setup.py`, just `import freebase` in your project and you're set.

If you want a working example, check out [Freebase Images](http://freebase-images.appspot.com). Its code is [in the repository](http://code.google.com/p/freebase-python/source/browse/#svn/trunk/examples/freebase-images-appengine).

# Overview #
[The README](http://freebase-python.googlecode.com/svn/trunk/examples/freebase-images-appengine/README) contains a simple description of the working parts of the freebase-images application. For a walkthrough of exactly how to make a Google AppEngine app, [see the creating a Google AppEngine with freebase-python walkthrough](AppEngineWalkthrough.md).

## Freebase Suggest ##
One neat thing you might notice if you visit the example is that you can start typing a topic, and suggestions will automatically pop up. This functionality is provided by the [Freebase suggest project](http://code.google.com/p/freebase-suggest/). It's really easy to include in your project. Once you download the zip and run `make` in the directory, you'll have a freebase.suggest.js as well as a css/ folder in a newly made dist/ folder. Put all of these in your project.

Freebase suggest uses [jQuery](http://jquery.com) so you'll have to include that too. Once you have jQuery, freebase.suggest.js, and the css files associated, all you have to do is tell jQuery what element you want to have suggest properties:
```
<script type="text/javascript">
  $(document).ready(function() {
    $("#id_of_element").freebaseSuggest();
  });
</script>
```
Naturally, there are many options you can pass freebaseSuggest(), all of which are detailed [here](http://code.google.com/p/freebase-suggest/wiki/Usage).

In the example application, the actual code was:
```
$("#q").freebaseSuggest().bind("fb-select", function(e, data) {
				id = data.id;
				window.location.hash = "#" + data.id;
				insert_images(data.id);	
			});
```