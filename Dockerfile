FROM python:3.11
ADD ./ /stormabot
WORKDIR /stormabot
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "/stormabot/main.py"]
