# set base image (host OS)
FROM python:3.9

# set the working directory in the container
WORKDIR /volley2

# copy the dependencies file to the working directory
COPY requirements.txt .

# copy the dependencies file to the working directory
COPY setup.py .

# set up the project to reference modules from the root
RUN pip install -e .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY api/ api/
COPY common/ common/

# command to run on container start
CMD flask --app api --debug run