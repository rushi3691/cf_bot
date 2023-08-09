FROM python:3.10.7-slim-bullseye

WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD [ "python3", "bot.py"]