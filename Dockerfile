FROM python:3.10
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN chmod 755 .
COPY . /app

CMD ["python", "run.py"]


