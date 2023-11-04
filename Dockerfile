FROM python:3.9-slim

WORKDIR /code

COPY ./app/dependencies.txt /code/app/dependencies.txt
COPY ../requirements.txt /code/requirements.txt

RUN python -m pip install --upgrade pip
RUN python -m pip install -r /code/app/dependencies.txt

COPY ./app/ /code/app
COPY ./app/.env /code/.env

EXPOSE 8000


#COPY wait-for-services.sh /wait-for-services.sh
#RUN chmod +x /wait-for-services.sh
#CMD ["/wait-for-services.sh", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
