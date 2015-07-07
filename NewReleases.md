# For Maintainers - Branching instructions (and updating pypi) #

1.0.x branches are supported entirely by branches/1.0.x, trunk is a new line of development
and should not be used to branch 1.0.x anything.

Otherwise, make changes to branches/1.0.x, branch to 1.0.n+1, commit.

Then, remove the 'tag\_build' line and set tag\_svn\_revision  to false.

AND THEN you're good to go,

python setup.py sdist upload