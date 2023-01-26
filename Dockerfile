FROM locustio/locust
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt