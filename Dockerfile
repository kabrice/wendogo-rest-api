FROM python:3.11
WORKDIR     /app
COPY ./requirements.txt /app/requirements.txt
COPY .env /app/.env
COPY . /app
RUN python3 -m pip install -r /app/requirements.txt

EXPOSE 80
EXPOSE 443
EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["app.py", "--host=0.0.0.0"]
