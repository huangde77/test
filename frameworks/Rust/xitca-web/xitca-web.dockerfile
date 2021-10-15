FROM rust:1.55

ADD ./ /xitca-web
WORKDIR /xitca-web

RUN rustup default nightly-2021-10-14
RUN cargo clean
RUN RUSTFLAGS="-C target-cpu=native" cargo build --release --bin xitca-web

EXPOSE 8080

CMD ./target/release/xitca-web
