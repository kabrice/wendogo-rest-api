FROM python:3.11
WORKDIR     /app
COPY ./requirements.txt /app/requirements.txt
COPY .env /app/.env
COPY . /app
RUN python3 -m pip install -r /app/requirements.txt
RUN apk add --no-cache ca-certificates

EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["app.py", "--host=0.0.0.0"]
