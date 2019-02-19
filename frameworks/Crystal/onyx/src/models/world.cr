require "pg"
require "onyx-sql"

class World
  include Onyx::SQL::Model

  schema world do
    pkey id : Int32
    type randomNumber : Int32
  end
end
