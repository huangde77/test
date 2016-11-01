local json = require "json"
local database = require "database"
local param = require "param"
local exit = require "exit"


local function process (db)
	ngx.header.content_type = 'application/json'
	
	local op = db:operators()
	
	local num_queries = tonumber(param.queries) or 1
	num_queries = math.min(500, num_queries)
	
	local worlds = {}
	for i=1, num_queries do
		local world = db:findOne({World = {id = op.equal(math.random(1,10000))}})
		world.randomnumber = math.random(1,10000)
		db:update({World = world})
		worlds[#worlds + 1] = world
	end
	
	if num_queries < 2 then
		return worlds[1]
	else
		return worlds
	end
end


local db = database.connect()
local status, res = pcall(process, db)
db:close()


if status then
	ngx.print(json.encode(res))
else
	exit(res)
end