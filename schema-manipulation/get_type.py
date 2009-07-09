# TODO: copy /freebase/type_hints junk
# TODO: preserve property order.

from pprint import pprint
import random
import json

from freebase.schema import TYPE_QUERY, PROPERTY_QUERY
from freebase.api  import HTTPMetawebSession, MetawebError

from freebase.schema import create_type, create_property, reciprocate_property, delegate_property

s = HTTPMetawebSession("http://sandbox-freebase.com")
s.login("nitromaster101@gmail.com", "something")

import time

def dump_base(s, base_id):
    types = map(lambda x: x["id"], s.mqlread({"id" : base_id, "/type/domain/types":[{"id" : None}]})["/type/domain/types"])
    graph = _get_graph(types)
    graph["__follow_types"] = True
    
    return graph

def dump_type(s, type_id, follow_types=True):
    types = [type_id]
    graph = _get_graph(types, follow_types)
    graph["__follow_types"] = follow_types
    result = json.dumps(graph, indent=2)
    
    fh = open("junk.json", "w")
    fh.write(result)
    fh.close()
    
    return graph
    

def upload_type(s, graph, new_location, ignore_types=None, debug=False):
    follow_types = graph.get("__follow_types", True)
    if debug: print "Following types:", follow_types
    
    # create type dependencies
    typegraph = {}
    for tid, idres in graph.items():
        if not tid.startswith("__"):
            typegraph[tid] = idres["__requires"]
    
    type_deps = map(lambda (name, x): (len(x), name), typegraph.items())
    type_deps.sort()
    if follow_types:
        types_to_create = create_what(type_deps, typegraph)
    else:
        types_to_create = typegraph.keys()
    
    # create property dependencies
    propgraph = {}
    proptotype = {}
    for tid, idres in graph.items():
        if not tid.startswith("__"):
            for prop in idres["properties"]:
                propgraph[prop["id"]] = prop["__requires"]
                proptotype[prop["id"]] = tid
    prop_deps = map(lambda (name, x): (len(x), name), propgraph.items())
    prop_deps.sort()
    if follow_types:
        props_to_create = create_what(prop_deps, propgraph)
    else:
        props_to_create = propgraph.keys()
    
    if debug: print "types", types_to_create
    if debug: print "-----------------------"
    if debug: print "props", props_to_create
    
    base_id, domain_id = s.mqlreadmulti([{"id" : types_to_create[0], "type" : "/type/type", "domain" : {"id" : None}},
                                         {"id" : new_location, "a:id" : None}])                         
    base_id = base_id["domain"]["id"]
    domain_id = domain_id["a:id"]
    
    only_include = types_to_create + props_to_create
    
    for type in types_to_create:
        if debug: print type
        key = ""
        if len(graph[type]["key"]) == 1:
            key = graph[type]["key"][0]["value"]
        else:
            expectedname = graph[type]["id"].split("/")[-1]
            if base_id:
                for group in graph[type]["key"]:
                    if group["namespace"] == base_id:
                        key = group["value"]
                        continue
            if key is None:
                key = expectedname
        tip = None
        if graph[type]["/freebase/documented_object/tip"]:
            tip = graph[type]["/freebase/documented_object/tip"]["value"]
        
        ignore = ("name", "domain", "key", "type", "id", "properties", "/freebase/type_hints/enumeration",
                    "/freebase/type_hints/included_types", "/freebase/type_hints/mediator", "/freebase/documented_object/tip")
        extra = {}
        for k, v in graph[type].items():
            if k not in ignore and not k.startswith("__"):
                if v:
                    if isinstance(v, basestring):
                        extra.update({k:v})
                    elif isinstance(v, bool):
                        extra.update({k:v})
                    elif v.has_key("id"):
                        extra.update({k:v["id"]})
                    elif v.has_key("value"):
                        extra.update({k:v["value"]})
                    else:
                        raise Exception("There is a problem with getting the property value.")
        
        create_type(s, graph[type]["name"]["value"], key, domain_id,
            included=map(lambda x: convert_name(x["id"], base_id, domain_id, only_include), graph[type]["/freebase/type_hints/included_types"]),
            cvt=graph[type]["/freebase/type_hints/mediator"],
            tip=tip, extra=extra)

    
    if debug: print "--------------------------"
    
    for prop in props_to_create:
        info = graph[proptotype[prop]]["properties"]
        for i in info:
            if i["id"] == prop: 
                
                schema = convert_name(proptotype[prop], base_id, domain_id, only_include)
                if debug: print prop
                expected = None
                
                if i["expected_type"]:
                    expected = convert_name(i["expected_type"], base_id, domain_id, only_include)
                for k in i["key"]:
                    if k.namespace == proptotype[prop]:
                        key = k.value
                if i["/freebase/documented_object/tip"]:
                    tip = graph[type]["/freebase/documented_object/tip"]
                
                disambig = i["/freebase/property_hints/disambiguator"]
                
                ignore = ("name", "expected_type", "key", "id", "master_property", "delegated", "unique", "type", "schema",
                            "/freebase/property_hints/disambiguator", "enumeration", "/freebase/property_hints/enumeration", 
                            "/freebase/documented_object/tip")
                extra = {}
                for k, v in i.items():
                    if k not in ignore and not k.startswith("__"):
                        if v:
                            if isinstance(v, basestring):
                                extra.update({k:v})
                            elif isinstance(v, bool):
                                extra.update({k:v})
                            elif v.has_key("id"):
                                extra.update({k:v["id"]})
                            elif v.has_key("value"):
                                extra.update({k:v["value"]})
                            else:
                                raise Exception("There is a problem with getting the property value.")
                            
                            # since we are creating a property, all these connect insert delicacies are unneccesary    
                            """if isinstance(v, basestring) and v.startswith("/"): # an id
                                extra.update({k : {"connect" : "insert", "id" : v}})
                            elif isinstance(v, bool): # a bool value
                                extra.update({k : {"connect" : "insert", "value" : v}})
                            else: # an english value
                                extra.update({k : {"connect" : "insert", "value" : v, "lang" : "/lang/en"}})"""
                
                
                if i['master_property']:
                    converted_master_property = convert_name(i["master_property"], base_id, domain_id, only_include)
                    if converted_master_property == i["master_property"]:
                        raise Exception("You can't set follow_types to False if there's a cvt. A cvt requires you get all the relevant types. Set follow_types to true.\n" + \
                                        "The offending property was %s, whose master was %s." % (prop["id"], prop["master_property"]))
                    reciprocate_property(s, i["name"], key, converted_master_property,
                        i["unique"], disambig=disambig, tip=tip, extra=extra)
                
                elif i['delegated']:
                    delegate_property(s, convert_name(i['delegated'], base_id, domain_id, only_include), schema,
                        expected=expected, tip=tip, extra=extra)
                
                else:
                    create_property(s, i["name"], key, schema, expected, i["unique"], 
                        disambig=disambig, tip=tip, extra=extra) 
                        
                
        
    


def _get_graph(initial_types, follow_types):
    """ get the graph of dependencies of all the types involved, starting with a list supplied """
    
    assert isinstance(initial_types, (list, tuple))
    
    graph = {}
    to_update = set(initial_types)
    done = set()
    while len(to_update) > 0:
        new = to_update.pop()
        graph[new] = _get_needed(s, new)
        if follow_types:
            [to_update.add(b) for b in graph[new]["__related"] if b not in done]
            done.update(graph[new]["__related"])
        if not follow_types:
            # we have to check that there are no cvts attached to us, or else
            # ugly things happen (we can't include the cvt)
            for prop in graph[new]["properties"]:
                if prop["master_property"]:
                    raise Exception("You can't set follow_types to False if there's a cvt. A cvt requires you get all the relevant types. Set follow_types to true.\n" + \
                                    "The offending property was %s, whose master was %s." % (prop["id"], prop["master_property"]))
    return graph

"""def create_type_dependencies(s, base_id=None, type_id=None, follow_types=True):
    
    if base_id:
        q = {"id" : base_id, "/type/domain/types" : [{"id" : None}] }
        results = s.mqlread(q)
        types = map(lambda x: x["id"], results["/type/domain/types"])
        #pprint(types)
    
    if type_id:
        types = [type_id]
        base_id = "/".join(type_id.split("/")[:-1])
        print base_id
    
    if not base_id and not type_id:
        raise Exception("You need to supply either a base_id or a type_id")
    
    graph = get_graph(types, follow_types)

    # find distinct subgraphs (looking at needs)
    subgraphs = []
    unknown = set(graph.keys())
    if focus:
        unknown = set([focus])
    while len(unknown) > 0:
        visited = set()
        to_visit = set([list(unknown)[0]])
        while len(to_visit) > 0:
            new = to_visit.pop()
            visited.add(new)
            try:
                unknown.remove(new)
            except KeyError:
                pass
            [to_visit.add(b) for b in graph[new]["related"] if b not in visited]
        subgraphs.append(list(visited))

    
    print "SUBGRPAHS"
    pprint(subgraphs)
    print "GRAPH"
    pprint(graph)
    return
    
    # create type dependencies
    typegraph = {}
    for tid, idres in graph.items():
        typegraph[tid] = idres["needs"]
    
    least_needy_type = map(lambda (name, x): (len(x), name), typegraph.items())
    least_needy_type.sort()
    
    types_to_create = create_what(least_needy_type, typegraph)
    
    # create property dependencies
    propgraph = {}
    proptotype = {}
    for tid, idres in graph.items():
        for prop in idres["properties"]:
            propgraph[prop["id"]] = prop["needs"]
            proptotype[prop["id"]] = tid
    least_needy = map(lambda (name, x): (len(x), name), propgraph.items())
    least_needy.sort()
    
    props_to_create = create_what(least_needy, propgraph)
    
    # CREATING STUFF
    
    domainname = "awesome" + str(int(random.random() * 1e10))
    print "\ndomainid", domainname
    print "--------------------------"
    dn = s.create_private_domain(domainname, domainname + "!")
    domain_id = dn.domain_id
    
    better_id = s.mqlread({"id" : domain_id, "a:id" : None})
    domain_id = better_id["a:id"]
    
    for type in types_to_create:
        print type
        key = ""
        if len(graph[type]["key"]) == 1:
            key = graph[type]["key"][0]["value"]
        else:
            expectedname = graph[type]["id"].split("/")[-1]
            if base_id:
                for group in graph[type]["key"]:
                    if group["namespace"] == base_id:
                        key = group["value"]
                        continue
            if key is None:
                key = expectedname
        tip = None
        if graph[type]["/freebase/documented_object/tip"]:
            tip = graph[type]["/freebase/documented_object/tip"]["value"]
        create_type(s, graph[type]["name"]["value"], key, domain_id,
            included=map(lambda x: convert_name(x["id"], base_id, domain_id), graph[type]["/freebase/type_hints/included_types"]),
            cvt=graph[type]["/freebase/type_hints/mediator"],
            enum=graph[type]["/freebase/type_hints/enumeration"],
            tip=tip)
    
    print "--------------------------"
    
    for prop in props_to_create:
        info = graph[proptotype[prop]]["properties"]
        for i in info:
            if i["id"] == prop: 
                schema = convert_name(proptotype[prop], base_id, domain_id)
                print prop
                expected = None
                if i["expected_type"]:
                    expected = convert_name(i["expected_type"]["id"], base_id, domain_id)
                for k in i["key"]:
                    if k.namespace == proptotype[prop]:
                        key = k.value
                if i["/freebase/documented_object/tip"]:
                    tip = graph[type]["/freebase/documented_object/tip"]
                    
                if i['master_property']:
                    reciprocate_property(s, i["name"], key, convert_name(i["master_property"]["id"], base_id, domain_id),
                        i["unique"], disambig=i["/freebase/property_hints/disambiguator"], tip=tip)
                elif i['delegated']:
                    delegate_property(s, convert_name(i['delegated']['id'], base_id, domain_id), schema,
                        expected=expected, tip=tip)
                else:
                    create_property(s, i["name"], key, schema, expected, i["unique"], 
                        disambig=i["/freebase/property_hints/disambiguator"], tip=tip) 
                        
                
        
    
    print "\ndomain id was", domainname
"""


def convert_name(old_name, operating_base, new_base, only_include=None):
    if old_name in only_include and old_name.startswith(operating_base):
        return new_base + old_name.replace(operating_base, "", 1)
    else:
        return old_name
    
def create_what(deps, graph):
    create_list = []
    while len(deps) > 0:
        neediness, id = deps.pop(0)
        if neediness == 0:
            create_list.append(id)
            continue
        else:
            work = True
            for req in graph[id]:
                if req not in create_list:
                    work = False
                    continue
            if work:
                create_list.append(id)
            else:
                deps.append((neediness, id))
    return create_list        
       


def _get_needed(s, type_id):
    q = TYPE_QUERY
    q.update(id=type_id)
    
    r = s.mqlread(q)
    properties = r.properties
    
    # let's identify who the parent is in order to only include
    # other types in that domain. We don't want to go around including
    # all of commons because someone's a /people/person
    parents = [r["domain"]["id"]]
   
    included_types = map(lambda x: x["id"], r["/freebase/type_hints/included_types"])
    related_types = set(included_types)
    for prop in properties:
        if prop["expected_type"]:
            related_types.add(prop["expected_type"])
    
    # we have two different types of relationships: required and related.
    # related can be used to generate subgraphs of types
    # required is used to generate the dependency graph of types
        
    related = return_relevant(related_types, parents)
    requires = return_relevant(included_types, parents)
    
    # get property information
    properties = r["properties"]
    for prop in properties:
        dependent_on = set()
        if prop["master_property"]:
            dependent_on.add(prop["master_property"])
        if prop["delegated"]:
            dependent_on.add(prop["delegated"])
        
        prop["__requires"] = return_relevant(dependent_on, parents)
    
    # return all the information along with our special __* properties
    info = r
    info.update(__related=related, __requires=requires, __properties=properties)
    
    return info
    

def return_relevant(start_list, parents):
    final = []
    for item in start_list:
        indomain = False
        for parent in parents:
            if item.startswith(parent):
                indomain = True
                continue
        if indomain:
            final.append(item)
    return final

if __name__ == '__main__':
    
    # create domain
    name = str(int(random.random()*1e10))
    domain_id = s.create_private_domain("coolcat" + name, "Coolcat" + name)["domain_id"]
    domain_id = s.mqlread({"id" : domain_id, "a:id" : None})["a:id"]
    print "domain name", domain_id

    # dump information
    #graph = dump_type(s, "/user/nitromaster101/coolcat3194242218/bridge_player", follow_types=True)
    graph = dump_type(s, "/people/person", True)
    
    # upload it somewhere else
    upload_type(s, graph, domain_id, debug=True)
    
    
    print "domain name", domain_id
    #create_type_dependencies(s, type_id="/base/contractbridge/bridge_player")
    
    
