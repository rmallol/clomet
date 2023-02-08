# build docker (inside Clomet_v0 folder): docker build -t clomet_v0 .
# run docker container: docker run -it -p 8000:8000 clomet_v0
# delete docker container: docker rmi -f clomet_v0


FROM python:3.8 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


COPY requirements.txt requirements.txt

RUN python -m pip install pip==22.0.4

RUN pip install -r requirements.txt

WORKDIR /usr/src/app

COPY . .

#RUN wget -q --continue "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
#RUN apt install ./google-chrome-stable_current_amd64.deb



RUN apt-get install -y wget unzip

# Set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Update the package list and install chrome
RUN apt-get update -y
RUN apt-get install -y google-chrome-stable


# Download and install Chromedriver
RUN wget  -q --continue "https://chromedriver.storage.googleapis.com/110.0.5481.77/chromedriver_linux64.zip"

RUN unzip chromedriver*
RUN chmod a+x chromedriver

# Put Chromedriver into the PATH
ENV PATH $CHROMEDRIVER_DIR:$PATH

EXPOSE 8000
STOPSIGNAL SIGTERM

CMD [ "python3", "manage.py", "runserver", "0:8000"]


