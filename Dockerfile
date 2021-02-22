FROM python:3.9-slim

RUN echo 'deb [check-valid-until=no] http://archive.debian.org/debian jessie-backports main' >> /etc/apt/sources.list \
    && apt-get update && apt-get install -y netcat make && apt-get autoremove -y


ENV PIP_FORMAT=legacy
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /imalive/
COPY . /imalive

RUN make install-production

# Create unprivileged user
RUN groupadd --non-unique --gid 1337 faust && useradd -u 1337 -m -s /bin/bash --gid 1337 faust
RUN chown -R faust:faust /imalive
USER faust

ENTRYPOINT ["./scripts/run"]
