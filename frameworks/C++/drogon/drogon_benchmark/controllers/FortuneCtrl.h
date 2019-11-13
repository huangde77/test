#pragma once
#include <drogon/HttpSimpleController.h>
#include <drogon/IOThreadStorage.h>

using namespace drogon;
class FortuneCtrl : public drogon::HttpSimpleController<FortuneCtrl>
{
  public:
    virtual void asyncHandleHttpRequest(
        const HttpRequestPtr &req,
        std::function<void(const HttpResponsePtr &)> &&callback) override;
    PATH_LIST_BEGIN
    // list path definitions here;
    PATH_LIST_END
  private:
    IOThreadStorage<orm::DbClientPtr> _dbClient;
};
