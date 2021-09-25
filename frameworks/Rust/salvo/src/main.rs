#[global_allocator]
static ALLOC: snmalloc_rs::SnMalloc = snmalloc_rs::SnMalloc;
// #[global_allocator]
// static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

#[macro_use]
extern crate serde_derive;
extern crate serde_json;

use salvo::http::header::{self, HeaderValue};
use salvo::prelude::*;

mod server;

static HELLO_WORLD: &'static [u8] = b"Hello, world!";
#[derive(Serialize)]
pub struct Message {
    pub message: &'static str,
}

#[fn_handler]
async fn json(res: &mut Response) {
    res.headers_mut().insert(header::SERVER, HeaderValue::from_static("S"));
    res.render_json(&Message {
        message: "Hello, World!",
    });
}

#[fn_handler]
async fn plaintext(res: &mut Response) {
    res.headers_mut().insert(header::SERVER, HeaderValue::from_static("S"));
    res.render_binary(HeaderValue::from_static("text/plain"), HELLO_WORLD);
}

fn main() {
    for _ in 1..num_cpus::get() {
        std::thread::spawn(move || {
            let rt = tokio::runtime::Builder::new_current_thread()
                .enable_all()
                .build()
                .unwrap();
            rt.block_on(serve());
        });
    }
    let rt = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .unwrap();
    rt.block_on(serve());
}

async fn serve() {
    println!("Started http server: 127.0.0.1:8080");
    let router = Router::new()
        .push(Router::new().path("plaintext").get(plaintext))
        .push(Router::new().path("json").get(json));

    server::builder()
        .http1_pipeline_flush(true)
        .serve(Service::new(router))
        .await
        .unwrap();
}
