FROM python:3.9
WORKDIR /app/src

# TODO: いろいろ試したけど，docker上からl2pingするのが難しそうなので，開発環境では送った定のコードを記述
# RUN apt-get update && apt-get -y install bluetooth && \
#     rm -rf /var/lib/apt/list/* /var/cache/apt/archives/* && \
#     apt-get clean
RUN pip install --upgrade pip && pip install --upgrade setuptools && pip install slack-bolt aiohttp