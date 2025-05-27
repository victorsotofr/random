# Summarize emails

I created this little `summarize.py` file to get a quick view of the key news (the `main.py` file is used for my automation deployed as a daily Cloud Function).

Indeed, I'm receiving quite a lot of newsletters and didn't want to unsuscribe, but rather get the most out of them quite quickly (FOMO effect...).

What is does: **fetches** all Gmail messages from today with the label news + **summarizes** them accurately using GPT-4o (with map-reduce to ensure factual recall), and clusters them into 2–6 clear, themed sections.

Each theme includes a headline + 3–8 bullet points with key numbers and facts + A sources line referencing the original emails.

The summary will be to me each day at 12am to my email adress.

---

```bash
pip install openai markdown2 google-api-python-client google-auth google-auth-oauthlib python-dotenv
```

Also ensure you have:

- A Google Cloud project

- `credentials.json` (OAuth 2.0 Client ID for Desktop App)

- An OpenAI API key (sk-...)

---

### Cloud Deployment

I deployed the automation so that the sending of the summary is triggered each day at 12:00 PM (Paris time) by Cloud Scheduler.

Once deployed, the function:

1. Fetches and summarizes emails labeled news using GPT-4o

2. Sends the digest to your Gmail inbox using the Gmail API

It runs daily at 12:00 PM Europe/Paris via Cloud Scheduler + uses Secret Manager to securely manage the `OPENAI_API_KEY` and `token.json`

The full logic is in `main.py` and deployed as a **Gen2 Cloud Function** with:

`gcloud functions deploy summarize_digest`

`gcloud scheduler jobs create http daily-news-digest`