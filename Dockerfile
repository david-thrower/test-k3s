FROM python:3.9.16-bullseye
RUN pip3 install --upgrade pip
COPY . .
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3", "app.py"]
