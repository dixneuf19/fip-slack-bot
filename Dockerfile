FROM python:3.11-buster@sha256:3a19b4d6ce4402d11bb19aa11416e4a262a60a57707a5cda5787a81285df2666

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY fip_slack_bot fip_slack_bot

EXPOSE 3000

CMD ["uvicorn", "fip_slack_bot.main:api" , "--host", "0.0.0.0", "--port", "3000"]
