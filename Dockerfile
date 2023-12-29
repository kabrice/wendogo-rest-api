FROM python:3.11
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
#COPY .env /app/.env
#COPY . ./app
RUN python3 -m pip install -r /app/requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
