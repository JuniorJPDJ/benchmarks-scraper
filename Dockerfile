FROM        python:3.13.3-alpine@sha256:452682e4648deafe431ad2f2391d726d7c52f0ff291be8bd4074b10379bb89ff

# renovate: datasource=repology depName=alpine_3_21/gcc versioning=loose
ARG         GCC_VERSION="14.2.0-r4"
# renovate: datasource=repology depName=alpine_3_21/build-base versioning=loose
ARG         BUILD_BASE_VERSION="0.5-r3"
# renovate: datasource=repology depName=alpine_3_21/libffi-dev versioning=loose
ARG         LIBFFI_VERSION="3.4.7-r0"

ARG         TARGETPLATFORM

WORKDIR     /app

ADD         requirements.txt .

RUN         --mount=type=cache,sharing=locked,target=/root/.cache,id=home-cache-$TARGETPLATFORM \
            apk add --no-cache --virtual .build-deps \
              gcc=${GCC_VERSION} \
              build-base=${BUILD_BASE_VERSION} \
              libffi-dev=${LIBFFI_VERSION} \
            && \
            pip install -r requirements.txt && \
	          apk del .build-deps && \
            chown -R nobody:nogroup /app

COPY        --chown=nobody:nogroup . .

USER        nobody
EXPOSE      9999

ENTRYPOINT  [ "python", "web_server.py" ]
