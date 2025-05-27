# Summarize emails

I created this little `summarize.py` file to get a quick view of the key news.

Indeed, I'm receiving quite a lot of newsletters and didn't want to unsuscribe, but rather get the most out of them quite quickly (FOMO effect...).

What is does: **fetches** all Gmail messages from today with the label news + **summarizes** them accurately using GPT-4o (with map-reduce to ensure factual recall), and clusters them into 2–6 clear, themed sections.

Each theme includes a headline + 3–8 bullet points with key numbers and facts + A sources line referencing the original emails.

The summary will be to me each day at 12am to my email adress.

---

```bash
pip install openai google-api-python-client google-auth google-auth-oauthlib python-dotenv
```

Also ensure you have:

- A Google Cloud project

- `credentials.json` (OAuth 2.0 Client ID for Desktop App)

- An OpenAI API key (sk-...)