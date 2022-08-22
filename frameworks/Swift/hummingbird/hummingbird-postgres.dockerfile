# ================================
# Build image
# ================================
FROM swift:5.6-focal as build
WORKDIR /build

# Copy entire repo into container
COPY ./src-postgres .

# Compile with optimizations
RUN swift build \
	-c release \
	-Xswiftc -enforce-exclusivity=unchecked

# ================================
# Run image
# ================================
FROM swift:5.6-focal-slim
WORKDIR /run

# Copy build artifacts
COPY --from=build /build/.build/release /run

ENV SERVER_PORT=8080
ENV SERVER_HOSTNAME=0.0.0.0

EXPOSE 8080

CMD ["./server"]
