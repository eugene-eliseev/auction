FROM python:3.6
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ADD ./static /static
COPY models.py .
COPY main.py .
COPY lang.py .
COPY items.txt .
COPY api_worker.py .
COPY functions.py .
CMD python main.py
