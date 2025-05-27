# Summarize emails

I created this little summarizing .py file to get a quick view of the key news, since I am receiving quite a lot of newsletter and don't want to unsuscribe (FOMO effect...)

**fetches** all Gmail messages from today with the label news + **summarizes** them accurately using GPT-4o (with map-reduce to ensure factual recall), and clusters them into 2–6 clear, themed sections.

Each theme includes a headline + 3–8 bullet points with key numbers and facts + A sources line referencing the original emails

---

```bash
pip install openai google-api-python-client google-auth google-auth-oauthlib python-dotenv
```

Also ensure you have:

- A Google Cloud project

- `credentials.json` (OAuth 2.0 Client ID for Desktop App)

- An OpenAI API key (sk-...)