# ebstar

A poor man's tool for searching for Star Alliance award availability in the
EuroBonus program.

This project consists of two parts: a **crawler** that allows you to
systematically crawl availability through SAS' Star Alliance award search page;
and a Jupyter notebook that allows you to **query** the crawled results.

## Crawling

> **Note**
> Consider using a VPN when running the crawler.

### Starting the cookie server

Start the cookie server. This is a server that will receive the most recent
cookie from your web browser and make it available to the crawler.

```
$ flask --app cookieserver run
```

### Send cookies to the cookie server

Open a new (incognito) tab in your web browser and open [SAS' Star Alliance
search
page](https://www.sas.se/book/flights/?search=OW_HKG-MUC-20221102_a1c0i0y0&view=upsell&bookingFlow=star&origin=eurobonus%252Fstar-alliance-award-trips%252F&outSort=stop&inSort=stop&outFilter=all&inFilter=all).
Don't bother logging in with your EuroBonus account.

When the page has loaded, run the following code in the tabs' developer console:

```
window.setInterval(() => { new Image().src = 'http://localhost:5000/?cookie=' + encodeURIComponent(document.cookie); }, 5000);
```

This will periodically send the cookie from your tab to the cookie server,
thereby ensuring that your traffic doesn't get classified as originating from
a bot.

### Start crawling

Now you're ready to start crawling. Say you want to go from CPH to SIN, TYO
or KUL in February 2023.

```
$ python3 ./crawler.py --origins=CPH --destinations=SIN,TYO,KUL --start=20230201 --end=20230228
IP address: XXX.XXX.XXX.XXX
Sending sample request ... success
Route(iata_from='CPH', iata_to='TYO', date='20230216') (168 routes left) 8220 ms ✓
Route(iata_from='CPH', iata_to='SIN', date='20230223') (167 routes left) 5583 ms ✓
Route(iata_from='CPH', iata_to='KUL', date='20230218') (166 routes left) 3058 ms ✓
Route(iata_from='TYO', iata_to='CPH', date='20230206') (165 routes left) 4191 ms ✓
Route(iata_from='KUL', iata_to='CPH', date='20230202') (164 routes left) 2242 ms ✓
Route(iata_from='TYO', iata_to='CPH', date='20230210') (163 routes left) 5412 ms ✓
Route(iata_from='CPH', iata_to='SIN', date='20230215') (162 routes left) 7154 ms ✓
...
```

The results are written to a SQLite database called `flights.db`.

If the crawler is too slow for your tastes, you can simply start another
crawler with the same parameters. In my experience, running four crawlers at
the same time is fine. Running more than four might result in your traffic
being classified as a bot.

## Querying the results

Start a Jupyter notebook server and then open [Query.ipynb](Query.ipynb), which
shows an example of how to query the results.
