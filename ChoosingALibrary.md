# Introduction #

The freebase-python project currently has two completely separate
Python libraries for accessing Freebase.com.
Both are supported, both are being used in real projects, but they are
different and it's quite likely that one supports your needs better than the other.

# Features common to both libraries #

XXX Fill this in XXX

# Advantages of metaweb-py #

  * metaweb-py is a single file, which is probably simpler to import if you have a small project.
  * metaweb-py supports search and readmulti()

# Advantages of freebase-api #

  * freebase-api is packaged as a python module using setuptools, which should make it easier to use in large applications
  * freebase-api uses httplib2, which has better HTTP 1.1 support and may be faster for large operations
  * freebase-api supports the trans() and upload() services