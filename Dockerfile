FROM python:3.8

WORKDIR /app

COPY techtrends /app

# RUN requirements
# initialize the database
RUN pip install -r requirements.txt
RUN python3 init_db.py

EXPOSE 3111

CMD [ "python3", "app.py" ]
