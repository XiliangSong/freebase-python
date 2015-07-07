# Problem #
While Sandbox (sandbox-freebase.com) is an excellent place to test your ideas without messing up the real freebase database, it is refreshed every Monday. If your changes are just small tests in order to test freebase writing, this is no problem. But if you develop schemas in sandbox, this sucks. This recipe will show you how to make your types survive the sandbox refresh.

# Solution (python) #
We will be using the latest version of freebase-python. We will be using some of the schema manipulation features which were introduced in version 1.0.

In order to prevent all the schemas from being erased, we have to download a copy to our local machines. Once the refresh has occurred, we should upload the schema to the desired location. We will be using two functions, `dump_base` and `restore`.

```
import freebase, freebase.schema
import json # or simplejson or jsonlib2

# For schema manipulation, we can't use freebase.funcname syntax.
# Instead, we have to make an HTTPMetawebSession
s = freebase.api.HTTPMetawebSession("http://sandbox-freebase.com")
s.login("andrew", "secret")

graph = freebase.schema.dump_base(s, "/base/mytestbase")

# save the file!
jsondump = json.dumps(graph, indent=2)
fh = open("mytestbase.schema.json", "w")
fh.write(jsondump)
fh.close()

# ... sandbox refresh ...
# create an empty base in sandbox

# upload the base
freebase.schema.restore(s, graph, "/base/mytestbase")
```

This example is very basic, but it shows the general idea of `dump_base` and `restore`.

Now you can do all sorts of things: you could edit the `mytestbase.schema.json` file (it's pretty straightforward`*`), you could keep different versions of your schemas and see the changes over time, or you could share your file with others.

`*` Please beware when editing the json file. It isn't `mql`. It resembles a mqlread result with a few special properties that aid it in reconstructing the schemas. While changing the uniqueness of a property is easy (true to false), adding entire new properties requires one to be sure of what they are doing. While drastically editing the output file isn't forbidden, please keep a backup of the original dump.

Do note, that although this recipe only covers saving a base from a sandbox refresh, you can do the same thing for types. The only difference is that you should use `dump_type` instead of `dump_base`. For more information, check out the ForkType page, which gives more information on copying types.

# Solution (command line) #
Even if you aren't as familiar with python, this tool can be accessed with a command line program, `fcl`, which is installed when you `easy_install freebase`.
```
andrew ~ $ fcl dump_base /base/contractbridge > contractbridge-07-17-09.json
andrew ~ $ fcl -S login nitromaster101
freebase.com password: 
andrew ~ $ fcl -S restore /base/mynewbase contractbridge-07-17-09.json 
```
The first command dumps the base `/base/contractbridge` into the contractbridge-07-17-09.json file. Next, we login to sandbox (specified by the `-S` flag). And finally, we restore our contractbridge-07-17-09.json file into a new base _on sandbox_, `/base/mynewbase`. Again, the `-S` flag specifies sandbox.