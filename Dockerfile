FROM python:3.13-alpine3.20@sha256:40a4559d3d6b2117b1fbe426f17d55b9100fa40609733a1d0c3f39e2151d4b33

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./bot.py" ]