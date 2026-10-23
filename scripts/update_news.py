"""Collect public RSS/Atom metadata; keep prior data on partial outages."""
import json,re,time,os,urllib.request,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
ROOT=Path(__file__).resolve().parents[1]
FEEDS=[('中国新闻','中国','https://news.google.com/rss/search?q='+urllib.parse.quote('BIM 建筑信息模型 when:7d')+'&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'),('国际新闻','国际','https://news.google.com/rss/search?q='+urllib.parse.quote('"building information modeling" OR "openBIM" when:7d')+'&hl=en-US&gl=US&ceid=US:en'),('arXiv科研','科研','https://export.arxiv.org/api/query?search_query=all:%22building%20information%20modeling%22&sortBy=submittedDate&sortOrder=descending&max_results=20')]
def clean(s):return re.sub('<[^>]+>',' ',s or '').strip()
def fetch(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'BIMDaily/1.0 (public research/news feed reader)'}),timeout=30) as r:return ET.fromstring(r.read(5_000_000))
        except Exception:
            if attempt==2:raise
            time.sleep(3*(attempt+1))
def parse(root,region):
    atom={'a':'http://www.w3.org/2005/Atom'};entries=root.findall('.//item') if region!='科研' else root.findall('a:entry',atom)
    out=[]
    for e in entries[:25]:
        if region=='科研':
            get=lambda k:e.findtext('a:'+k,'',atom)
            title=' '.join(get('title').split());url=get('id').replace('http:','https:');date=get('published')[:10]
            summary='预印本 · 原文摘要（未自动翻译）：\n'+' '.join(get('summary').split())[:1800];source='arXiv · 预印本，同行评审状态未核验'
        else:
            get=lambda k:e.findtext(k,'')
            title=clean(get('title'));url=get('link');date=parsedate_to_datetime(get('pubDate')).date().isoformat();source=get('source') or 'Google News RSS';summary='新闻索引 · 点击原文阅读完整报道，当前未生成自动中文摘要。'
        if not title or not url.startswith('https://'):continue
        tag='科研资讯' if region=='科研' else '政策标准' if re.search('标准|政策|IFC|standard|mandate',title,re.I) else '软件动态' if re.search('Revit|Autodesk|Bentley|软件|software',title,re.I) else '行业活动' if re.search('峰会|会议|summit|award|conference',title,re.I) else '项目应用'
        out.append(dict(title=title,url=url,date=date,source=source,summary=summary,region=region,tag=tag,live=True,research=region=='科研'))
    return out

def main():
    path=ROOT/'data/news.json';old=json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {'items':[]};items=[];statuses=[];success=0
    now=datetime.now(timezone.utc).isoformat()
    for name,region,url in FEEDS:
        try:
            rows=parse(fetch(url),region)
            if not rows:raise ValueError('No valid feed entries')
            items.extend(rows);success+=1;statuses.append(dict(name=name,status='成功',count=len(rows),checkedAt=now))
        except Exception as exc:
            print(name, type(exc).__name__);statuses.append(dict(name=name,status='采集失败，保留历史',checkedAt=now))
    # Historical records remain available even if a feed is temporarily empty.
    items.extend(old.get('items',[]));seen=set();unique=[]
    for x in items:
        key=x['url']
        if key not in seen:seen.add(key);unique.append(x)
    unique.sort(key=lambda x:x.get('date',''),reverse=True)
    data=dict(items=unique[:250],updatedAt=now if success else old.get('updatedAt'),lastAttemptAt=now,sources=statuses)
    path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    if success:
        archive=ROOT/'data/archive';archive.mkdir(exist_ok=True);(archive/(now[:10]+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Sources succeeded:',success,'Items:',len(data['items']))
    if not success:raise SystemExit(1)
if __name__=='__main__':main()
