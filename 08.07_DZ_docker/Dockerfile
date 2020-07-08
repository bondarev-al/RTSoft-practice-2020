FROM python:3.8.3-alpine3.11
LABEL maintainer="Alexander Bondarev <bondarev-al@mail.ru>"
LABEL description="This Dockerfile install alpine with python and copy file README in image."
RUN apk add bash
COPY ./README /README
ENTRYPOINT ["bash"]