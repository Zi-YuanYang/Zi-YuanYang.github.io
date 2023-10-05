import json
import requests
from bs4 import BeautifulSoup


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Not;A=Brand";v="8", "Chromium";v="117", "Google Chrome";v="117"',
    "Sec-Ch-Ua-Arch": '"x86"',
    "Sec-Ch-Ua-Bitness": '"64"',
    "Sec-Ch-Ua-Full-Version-List": '"Not;A=Brand";v="8.0.0.0", "Chromium";v="117.0.5938.92", "Google Chrome";v="117.0.5938.92"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Model": '""',
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Ch-Ua-Platform-Version": '"15.0.0"',
    "Sec-Ch-Ua-Wow64": "?0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

url = 'https://scholar.google.com/citations?user=2vZsJskAAAAJ&hl=zh-CN'
r = requests.get(url, headers=headers)

bs = BeautifulSoup(r.text, "html.parser")

papers = bs.select("#gsc_a_b > tr")

paper_to_citation = {}

for paper in papers:
    # print(paper)
    
    title = paper.find("a").text.lower()
    citation = paper.select(".gsc_a_ac")[0].text


    citation = int(citation) if citation != "" else 0
    paper_to_citation[title] = citation

node = bs.select("#gsc_rsb_cit")[0].select("div.gsc_g_hist_wrp")[0].select("div.gsc_md_hist_b")[0]

years = []
citations = []

for node in node.select("span"):
    year = node.text
    years.append(year)

n = len(years)
citations = years[-n//2:]
citations = list(map(lambda x: int(x) if x!= "" else 0, citations))
years = years[:-n//2]

print(years)
print(citations)

data = {
    "paper": paper_to_citation,
    "years": years,
    "citations": citations
}

data = json.dumps(data)

import os
if not os.path.exists("./google/"):
    os.mkdir("./google")

with open("./google/data.json", "w", encoding="utf-8") as f:
    f.write(data)


