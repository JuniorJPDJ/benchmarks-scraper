FROM        python:3.13.5-alpine@sha256:37b14db89f587f9eaa890e4a442a3fe55db452b69cca1403cc730bd0fbdc8aaf

# renovate: datasource=repology depName=alpine_3_22/gcc versioning=loose
ARG         GCC_VERSION="14.2.0-r6"
# renovate: datasource=repology depName=alpine_3_22/build-base versioning=loose
ARG         BUILD_BASE_VERSION="0.5-r3"
# renovate: datasource=repology depName=alpine_3_22/libffi-dev versioning=loose
ARG         LIBFFI_VERSION="3.4.8-r0"

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
