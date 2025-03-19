FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .

RUN yum install git tar zip gzip -y
RUN pip install -r requirements.txt 

COPY src.tar.gz ./

CMD ["app.handler"]
