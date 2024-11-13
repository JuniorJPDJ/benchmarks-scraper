FROM        python:3.13.0-alpine@sha256:fcbcbbecdeae71d3b77445d9144d1914df55110f825ab62b04a66c7c33c09373

# renovate: datasource=repology depName=alpine_3_20/gcc versioning=loose
ARG         GCC_VERSION="13.2.1_git20240309-r0"
# renovate: datasource=repology depName=alpine_3_20/build-base versioning=loose
ARG         BUILD_BASE_VERSION="0.5-r3"
# renovate: datasource=repology depName=alpine_3_20/libffi-dev versioning=loose
ARG         LIBFFI_VERSION="3.4.6-r0"

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
