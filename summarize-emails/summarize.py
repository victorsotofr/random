import os
from dotenv import load_dotenv
import json
import datetime
from openai import OpenAI
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

#################################################################
# CONFIGURATION
#################################################################

load_dotenv()

LABEL = "news"
MAX_EMAILS = 50
model = "gpt-4o"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

##################################################################
# FUNCTIONS
##################################################################

# GMAIL AUTHENTICATION
def gmail_authenticate():
    creds = None
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# HELPERS
def plain_text_body(msg):
    """Return the best-effort plain-text of the email."""
    import base64, quopri, re, html
    parts = msg["payload"].get("parts", [msg["payload"]])
    for p in parts:
        if p["mimeType"].startswith("text/plain"):
            data = base64.urlsafe_b64decode(p["body"]["data"])
            return data.decode(p.get("headers", [{}])[0].get("charset", "utf-8"), "ignore")
    data = base64.urlsafe_b64decode(parts[0]["body"]["data"])
    text = html.unescape(re.sub(r"<[^>]+>", " ", data.decode("utf-8", "ignore")))
    return re.sub(r"\s+", " ", text).strip()

def split_chunks(text, size=10_000):
    for i in range(0, len(text), size):
        yield text[i:i+size]

# 1—MAP REDUCE PER EMAIL
def map_reduce_summarize(email_body: str) -> str:
    """Guarantees every fact survives even for very long newsletters."""
    chunks = list(split_chunks(email_body))
    partials = []
    for chunk in chunks:
        resp = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarise the following text in bullet points that keep EVERY concrete fact (numbers, names, dates)."
                        "Do not omit anything factual."
                        "Use short bullets."
                    ),
                },
                {"role": "user", "content": chunk},
            ],
        )
        partials.append(resp.choices[0].message.content)

    merged = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Merge the partial summaries into one coherent, de-duplicated list of facts.",
            },
            {"role": "user", "content": "\n\n".join(partials)},
        ],
    )
    return merged.choices[0].message.content

# 2—COLLECT FACTS FROM ALL TODAY'S EMAILS
def collect_email_facts(service):
    today = datetime.datetime.now().strftime("%Y/%m/%d")
    query = f"label:{LABEL} after:{today}"
    res = service.users().messages().list(userId="me", q=query, maxResults=MAX_EMAILS).execute()
    msgs = res.get("messages", [])
    summaries = []

    for m in msgs:
        full = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        subject = next(
            (h["value"] for h in full["payload"]["headers"] if h["name"] == "Subject"), "(No subject)"
        )
        body = plain_text_body(full)
        fact_list = map_reduce_summarize(body)
        summaries.append({"subject": subject, "facts": fact_list})
    return summaries

# 3-FINAL DIGEST
def final_digest(fact_packs):
    sys = (
        "You are writing a lunchtime news digest for a busy professional.\n"
        "Your task is to group email summaries into 2–6 clear THEMES.\n"
        "Merge topics that belong to the same sector (e.g. finance, AI, markets, health).\n\n"
        "For each theme, return:\n"
        "1. A **headline** — use a short noun phrase (2–5 words, no verbs)\n"
        "2. 3–8 bullet points — each ≤25 words, always include concrete facts (numbers, names, companies, events)\n"
        "3. A **Sources** line — list all contributing email subjects, comma-separated\n\n"
        "Return clean Markdown with:\n"
        "• Bold theme titles\n"
        "• Indented bullets\n"
        "• 1 blank line between themes\n"
        "You must preserve every factually meaningful point."
    )

    user = json.dumps(fact_packs, ensure_ascii=False)
    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        max_tokens=2000,
        messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}],
    )
    return resp.choices[0].message.content

# MAIN EXECUTION
if __name__ == "__main__":
    print("Authenticating with Gmail...")
    gmail = gmail_authenticate()
    print("Fetching today's emails labeled 'news'...")    
    email_summaries = collect_email_facts(gmail)

    if not email_summaries:
        print("No emails found for today.")
    else:
        print("Summarizing today's emails...")
        summary = final_digest(email_summaries)
        print(f"Recap of {datetime.date.today():%d %b %Y}:\n" + summary)
