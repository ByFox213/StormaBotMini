FROM python:3.11
ADD ./ /tw
WORKDIR /tw
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "/tw/main.py"]
