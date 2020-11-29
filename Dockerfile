FROM python:3.8-buster

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY fip_slack_bot fip_slack_bot

ENV PYTHONPATH=.

CMD ["python", "fip_slack_bot/main.py"]
