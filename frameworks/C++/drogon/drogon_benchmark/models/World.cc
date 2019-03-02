/**
 *
 *  World.cc
 *  DO NOT EDIT. This file is generated by drogon_ctl
 *
 */

#include "World.h"
#include <drogon/utils/Utilities.h>
#include <string>

using namespace drogon_model::hello_world;

const std::string World::Cols::id = "id";
const std::string World::Cols::randomnumber = "randomnumber";
const std::string World::primaryKeyName = "id";
const bool World::hasPrimaryKey = true;
const std::string World::tableName = "world";

const std::vector<typename World::MetaData> World::_metaData={
{"id","int32_t","integer",4,0,1,1},
{"randomnumber","int32_t","integer",4,0,0,1}
};
const std::string &World::getColumnName(size_t index) noexcept(false)
{
    assert(index < _metaData.size());
    return _metaData[index]._colName;
}
World::World(const Row &r) noexcept
{
        if(!r["id"].isNull())
        {
            _id=std::make_shared<int32_t>(r["id"].as<int32_t>());
        }
        if(!r["randomnumber"].isNull())
        {
            _randomnumber=std::make_shared<int32_t>(r["randomnumber"].as<int32_t>());
        }
}
const int32_t & World::getValueOfId(const int32_t &defaultValue) const noexcept
{
    if(_id)
        return *_id;
    return defaultValue;
}
std::shared_ptr<const int32_t> World::getId() const noexcept
{
    return _id;
}
void World::setId(const int32_t &id) noexcept
{
    _id = std::make_shared<int32_t>(id);
    _dirtyFlag[0] = true;
}

const typename World::PrimaryKeyType & World::getPrimaryKey() const
{
    assert(_id);
    return *_id;
}

const int32_t & World::getValueOfRandomnumber(const int32_t &defaultValue) const noexcept
{
    if(_randomnumber)
        return *_randomnumber;
    return defaultValue;
}
std::shared_ptr<const int32_t> World::getRandomnumber() const noexcept
{
    return _randomnumber;
}
void World::setRandomnumber(const int32_t &randomnumber) noexcept
{
    _randomnumber = std::make_shared<int32_t>(randomnumber);
    _dirtyFlag[1] = true;
}


void World::updateId(const uint64_t id)
{
}

const std::vector<std::string> &World::insertColumns() noexcept
{
    static const std::vector<std::string> _inCols={
        "id",
        "randomnumber"
    };
    return _inCols;
}

void World::outputArgs(drogon::orm::internal::SqlBinder &binder) const
{
    if(getId())
    {
        binder << getValueOfId();
    }
    else
    {
        binder << nullptr;
    }
    if(getRandomnumber())
    {
        binder << getValueOfRandomnumber();
    }
    else
    {
        binder << nullptr;
    }
}

const std::vector<std::string> World::updateColumns() const
{
    std::vector<std::string> ret;
    for(size_t i=0;i<sizeof(_dirtyFlag);i++)
    {
        if(_dirtyFlag[i])
        {
            ret.push_back(getColumnName(i));
        }
    }
    return ret;
}

void World::updateArgs(drogon::orm::internal::SqlBinder &binder) const
{
    if(_dirtyFlag[0])
    {
        if(getId())
        {
            binder << getValueOfId();
        }
        else
        {
            binder << nullptr;
        }
    }
    if(_dirtyFlag[1])
    {
        if(getRandomnumber())
        {
            binder << getValueOfRandomnumber();
        }
        else
        {
            binder << nullptr;
        }
    }
}
Json::Value World::toJson() const
{
    Json::Value ret;
    if(getId())
    {
        ret["id"]=getValueOfId();
    }
    else
    {
        ret["id"]=Json::Value();
    }
    if(getRandomnumber())
    {
        ret["randomnumber"]=getValueOfRandomnumber();
    }
    else
    {
        ret["randomnumber"]=Json::Value();
    }
    return ret;
}
