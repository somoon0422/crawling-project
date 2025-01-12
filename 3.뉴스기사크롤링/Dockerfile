FROM ubuntu:22.04

RUN apt-get update
# RUN apt-get install -y git
RUN apt-get install -y python3-pip


RUN apt -y install wget

RUN apt -y install unzip

RUN apt -y install curl

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

RUN apt -y install ./google-chrome-stable_current_amd64.deb

RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/` curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

RUN unzip /tmp/chromedriver.zip chromedriver -d /app/

WORKDIR /app

ARG UID=10001
# RUN adduser \
# --disabled-password \
# --gecos "" user \
# --no-create-home \
# --uid "${UID}" \
# user

# RUN chown -R appuser:appuser /root/

COPY . .

RUN python3 -m pip install -r requirements.txt

# USER appuser


EXPOSE 8501

CMD streamlit run streamlit_app.py