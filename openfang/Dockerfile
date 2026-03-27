# syntax=docker/dockerfile:1
# Build OpenFang from source with limited parallelism to stay within
# Docker Desktop memory limits.

FROM rust:1-slim-bookworm AS builder

ARG OPENFANG_REF=v1.0.0

WORKDIR /build
RUN apt-get update \
    && apt-get install -y --no-install-recommends git pkg-config libssl-dev ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch ${OPENFANG_REF} \
    https://github.com/RightNow-AI/openfang.git /build/openfang

WORKDIR /build/openfang
# Limit to 2 parallel rustc jobs to avoid OOM on constrained Docker hosts.
ENV CARGO_BUILD_JOBS=2
RUN cargo build --release --bin openfang

# --- runtime ---
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl libssl3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/openfang/target/release/openfang /usr/local/bin/openfang

EXPOSE 4200
VOLUME /data
ENV OPENFANG_HOME=/data

ENTRYPOINT ["openfang"]
CMD ["start"]
