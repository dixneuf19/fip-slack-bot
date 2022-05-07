FROM python:3.10-buster

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY fip_slack_bot fip_slack_bot

EXPOSE 3000

CMD ["uvicorn", "fip_slack_bot.main:api" , "--host", "0.0.0.0", "--port", "3000"]
