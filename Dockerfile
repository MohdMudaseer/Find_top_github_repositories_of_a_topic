# base image
FROM python:3.11

# set working directory
WORKDIR /wsgi

# copy project
COPY . /wsgi

# install dependencies
RUN pip install -r requirements.txt

# expose port
EXPOSE 5000

# run the application
CMD ["python", "app.py"]