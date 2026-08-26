# nutrition-irrigation-model-1.2.0

FROM python:3.9-slim-bookworm 
fgd
RUN mkdir -p /home/smart_benchmark/benchmark/datasets

WORKDIR /home/smart_benchmark
# Copy REQUIREMENT_FILE in src folder
COPY .  /home/smart_benchmark/

RUN apt-get update 
RUN apt-get install gcc -y 
RUN apt-get install -y --no-install-recommends git \
&& apt-get clean

RUN pip install -r /home/smart_benchmark/requirements.txt
RUN pip install --upgrade pip
RUN pip install flake8 black

# Set PYTHONPATH
ENV PYTHONPATH="/home/smart_benchmark:$PATH"
ENV TZ="Europe/Rome"
