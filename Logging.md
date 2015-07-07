# Introduction #

Logging is useful in changing the amount of information being outputted by the library. Sometimes you want to know absolutely every command being issued, sometimes you just want to write to a file the times when a query failed. Logging solves all these problems. Naturally, you can get familiar with all the logging options using the [logging module's page](http://docs.python.org/library/logging.html). But for a quick overview, this is the place to be.


# Logging to the Console #
```
import logging
import freebase

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

freebase.sandbox.log.setLevel(logging.DEBUG)
freebase.sandbox.log.addHandler(console)

result = freebase.sandbox.mqlread([dict(name=None, type='/type/type')])
```
We create a `console` object that outputs to the console. It has a debug level (`logging.DEBUG`). We also set the logging level for the logging object that inside the HTTPMetawebSession (discussed below). The logging level assigned to `freebase.sandbox` limits the library to only output at the level and higher. The logging level assigned to `console` sets what is printed (because this console prints to the screen). I could define another `StreamHandler` that had a different logging level, for, say, printing to a file.
```
import logging
import freebase

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

fileman = logging.FileHandler("freebase-python-problems.txt")
fileman.setLevel(logging.ERROR)

freebase.sandbox.log.setLevel(logging.DEBUG)
freebase.sandbox.log.addHandler(console)
freebase.sandbox.log.addHandler(fileman)

result = freebase.sandbox.mqlread([dict(name=None, type='/type/type')])
```
We'll talk about logging to a file a bit later.
## HTTPMetawebSession ##
As you have hopefully found out, both `freebase` and `freebase.sandbox` are wrappers for separate `HTTPMetawebSession`s. This example is very similar to the one before, but exposes the underlying `HTTPMetawebSession`.
```
import logging
from freebase.api import HTTPMetawebSession

mss = HTTPMetawebSession('sandbox.freebase.com')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

mss.log.setLevel(logging.DEBUG)
mss.log.addHandler(console)

result = mss.mqlread([dict(name=None, type='/type/type')])
```

# Logging to a File #
```
import logging
from freebase.api import HTTPMetawebSession

mss = HTTPMetawebSession('sandbox.freebase.com')

console = logging.FileHandler("logger-frogger.txt")
console.setLevel(logging.DEBUG)

mss.log.setLevel(logging.DEBUG)
mss.log.addHandler(console)

n = mss.mqlread([dict(name=None, type='/type/type')])
```
You can also use a [rotating file handler](http://docs.python.org/library/logging.html#rotatingfilehandler).