# Problem #
You just found this base that has an intriguing schema on old cameras. You have a few ideas on how to improve it because you've just worked on a few schemas for DSLR cameras. The problem is that it looks like the base's owner has totally forgotten about freebase and his base. How can you improve his schemas without hand copying each and every one?

# Solution #
Instead of hand copying each one, we'll use one of the schema manipulation functions in freebase-python.

```
import freebase, freebase.schema
s = freebase.api.HTTPMetawebSession("http://api.sandbox-freebase.com")
s.login("andrew", "secret")

graph = freebase.schema.dump_type(s, "/base/oldcameras/camera", follow_types=False)
restore(s, graph, "/base/mytestbase")
```

## What did we just do ##
  * Logged in to sandbox-freebase.com
  * Dumped the type /base/oldcameras/camera with follow\_types=False
  * Uploaded the type we just dumped into another base, specifically /base/mytestbase.

All of this is pretty straightforward (also similar to [making a base survive a sandbox refresh cycle](SandboxRefresh.md)) except for the `follow_types` argument.

The problem stems from the fact that when we want to copy a type (/base/oldcameras/camera), it is unclear what to do. Most types have `included_types` and most properties reference other objects in the graph (the freebase graph, or database). When copying a type, we have to make a certain judgement call on what to copy and what to leave. For example, say /base/oldcameras/camera has an included\_type of /common/topic. When we copy `camera`, we want to preserve this information, but we don't want to copy /common/topic into the new base since it's a global type that will always be there. So this case is obvious, we don't want to copy types that are always going to be there since that's unnecessary clutter. As a general rule, `dump_type` will not copy anything in /common. But what if we present a different example. `camera` has a property `film` whose `expected_type` is /base/oldcameras/film. Now, when we copy the `camera` type, do we also want to copy `film`, or not? This is what follow\_types dictates.

Now we present another issue that confounds everything. Say `camera` has a property `make` that links to a [cvt (compound value type)](http://www.freebase.com/view/en/compound_value_type_cvt_definition) /base/oldcameras/camera\_make. The way cvts work is that (in most cases), the cvt's properties link to objects and those objects have properties that reciprocate the cvt's links. If you want to see a canonical example, check out the relationship between /film/film and /film/performance. You will note that /film/performance/actor is a connection to an actor, which is reciprocated by /film/film/starring.

Anyways, back to the problem. If I try to copy the type `camera` that links to the cvt `camera_make` and set `follow_types` to `false`, `dump_type` will spit out an error. Let's examine the reasoning. If we were to create a `copy_camera` type in another base that had a property that instead of reciprocating `camera_make/camera` just linked to it, it would ruin the usefulness of the `make` property.

The last issue of this type is a rather specialized case, but it could still affect someone. Let's use the example of /people/person. Person has a property `education` which links in to the cvt /education/education. The problem here is that the cvt is another domain (/education v. /people). If this is the case, `dump_type` will always balk, even if `follow_types` is set to `True` because in this case, it is impossible to only copy schemas in /people and still make the cvt worthwhile. The only way you could replicate all of /people/person is to also copy all of /education! `dump_type` doesn't even start to get into this business, which could end up copying most of the freebase graph.

I apologize if this is too confusing, but it is a real issue to be aware of. If you want to sidestep the issue, just set follow\_types to True and you should be fine in most cases.