FROM python:3.10-buster@sha256:31a8498af27dba1f431f2df60189ca79ff5f440cfa7b6dea2da6ab15c74abcd4

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY fip_slack_bot fip_slack_bot

EXPOSE 3000

CMD ["uvicorn", "fip_slack_bot.main:api" , "--host", "0.0.0.0", "--port", "3000"]
