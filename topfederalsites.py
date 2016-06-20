import requests, psycopg2, os, urlparse, datetime

# Get credits from a local file
with open("creds.json") as f:
    creds = json.load(f)

# Start up tweepy
consumer_key = creds["consumer_key"]
consumer_secret = creds["consumer_secret"]
access_token = creds["access_token"]
access_token_secret = creds["access_token_secret"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# Set up database
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
cur = conn.cursor()

# Check the data
now_sites = requests.get("https://analytics.usa.gov/data/live/top-pages-realtime.json").json()
cur.execute("SELECT url FROM sites;")
old_sites = cur.fetchall()
for site in now_sites["data"]:
    if (site["page"],) in old_sites:
        pass
    else:
        print("new site: "+site["page"])
        time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        cur.execute("INSERT INTO sites (url, title, visitors, time) VALUES (%s, %s, %s, %s)",(site["page"],site["page_title"],str(site["active_visitors"]), time))
        if len(site["page_title"]) > 59:
            title = site["page_title"][0:58]+u'\u2026'
        else:
            title = site["page_title"]
        self.update_status("New site in the top 20! Welcome to %s (%s) with %s visitors" %\
            (site["page"],title,site["active_visitors"]))
conn.commit()
