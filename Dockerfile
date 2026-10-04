FROM        python:3.14.8-alpine@sha256:f6a589d43c42b9e7f7dc67a12d37132491f362859a5d750607710cc56da3bc72

# renovate: datasource=repology depName=alpine_3_24/gcc versioning=loose
ARG         GCC_VERSION="15.2.0-r5"
# renovate: datasource=repology depName=alpine_3_24/build-base versioning=loose
ARG         BUILD_BASE_VERSION="0.5-r4"
# renovate: datasource=repology depName=alpine_3_24/libffi-dev versioning=loose
ARG         LIBFFI_VERSION="3.5.2-r1"
# renovate: datasource=repology depName=alpine_3_24/cmake versioning=loose
ARG         CMAKE_VERSION="4.2.3-r0"

ARG         TARGETPLATFORM

WORKDIR     /app

ADD         requirements.txt .

RUN         --mount=type=cache,sharing=locked,target=/root/.cache,id=home-cache-$TARGETPLATFORM \
            apk add --no-cache --virtual .build-deps \
              gcc=${GCC_VERSION} \
              build-base=${BUILD_BASE_VERSION} \
              libffi-dev=${LIBFFI_VERSION} \
              cmake=${CMAKE_VERSION} \
            && \
            pip install -r requirements.txt && \
	          apk del .build-deps && \
            chown -R nobody:nogroup /app

COPY        --chown=nobody:nogroup . .

USER        nobody
EXPOSE      9999

ENTRYPOINT  [ "python", "web_server.py" ]
