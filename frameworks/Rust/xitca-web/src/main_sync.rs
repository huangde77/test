mod db_diesel;
mod schema;
mod ser;
mod util;

use serde::Serialize;
use xitca_web::{
    codegen::route,
    handler::{html::Html, json::Json, query::Query, state::StateOwn},
    http::{header::SERVER, WebResponse},
    App,
};

use db_diesel::Pool;
use ser::Num;
use util::{HandleResult, SERVER_HEADER_VALUE};

fn main() -> std::io::Result<()> {
    App::new()
        .with_state(db_diesel::create()?)
        .at_typed(plaintext)
        .at_typed(json)
        .at_typed(db)
        .at_typed(fortunes)
        .at_typed(queries)
        .at_typed(updates)
        .map(header)
        .serve()
        .bind("0.0.0.0:8080")?
        .run()
        .wait()
}

fn header(mut res: WebResponse) -> WebResponse {
    res.headers_mut().insert(SERVER, SERVER_HEADER_VALUE);
    res
}

#[route("/plaintext", method = get)]
fn plaintext() -> &'static str {
    "Hello, World!"
}

#[route("/json", method = get)]
fn json() -> Json<ser::Message> {
    Json(ser::Message::new())
}

#[route("/db", method = get)]
fn db(StateOwn(pool): StateOwn<Pool>) -> HandleResult<Json<impl Serialize>> {
    pool.get_world().map(Json)
}

#[route("/fortunes", method = get)]
fn fortunes(StateOwn(pool): StateOwn<Pool>) -> HandleResult<Html<String>> {
    use sailfish::TemplateOnce;
    pool.tell_fortune()?
        .render_once()
        .map(Html)
        .map_err(Into::into)
}

#[route("/queries", method = get)]
fn queries(
    Query(Num(num)): Query<Num>,
    StateOwn(pool): StateOwn<Pool>,
) -> HandleResult<Json<impl Serialize>> {
    pool.get_worlds(num).map(Json)
}

#[route("/updates", method = get)]
fn updates(
    Query(Num(num)): Query<Num>,
    StateOwn(pool): StateOwn<Pool>,
) -> HandleResult<Json<impl Serialize>> {
    pool.update(num).map(Json)
}
