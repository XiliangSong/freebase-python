# Problem #
After hours of toiling and perfecting your schema, you think it's downright snazzy. Hopefully, you've been working on your base in sandbox and [saving yourself from the sandbox refreshes](SandboxRefresh.md). Now you're ready to transfer the base into the "real" freebase production server so that anyone can use your cool schema and upload data.

# Solution #
This problem is actually almost identical to the SandboxRefresh. When we were surviving the sandbox refresh, we had to save the graph and wait until the refresh finished. In this case, we just grab the base in sandbox and put it in production.
```
import freebase, freebase.schema

sandbox = freebase.api.HTTPMetawebSession("http://api.sandbox.freebase.com")
sandbox.login("andrew", "secret")

production = freebase.api.HTTPMetawebSession("http://api.freebase.com")
sandbox.login("andrew", "secret")

graph = freebase.schema.dump_base(sandbox, "/base/mybase")
# create an empty base in production
freebase.schema.restore(production, graph, "/base/mybase")
```

Note, I haven't actually tried this in real life, but it should work since it is the exact same idea behind the SandboxRefresh.