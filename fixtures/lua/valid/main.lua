local version = meldritch.host_api_version()
assert(type(version) == "string")
local graph = meldritch.graph()
return graph
