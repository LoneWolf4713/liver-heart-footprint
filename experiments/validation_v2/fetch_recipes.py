import requests,json,re,time,sys,csv,urllib.robotparser as rp,urllib.parse as up,datetime
UA='Mozilla/5.0 (research; academic validation; contact aashish.jha@marbles.health)'
robots={}
def allowed(u):
    h=up.urlparse(u); b=f'{h.scheme}://{h.netloc}'
    if b not in robots:
        r=rp.RobotFileParser(); 
        try:
            t=requests.get(b+'/robots.txt',headers={'User-Agent':UA},timeout=20).text; r.parse(t.splitlines())
        except Exception as e: r.parse([])
        robots[b]=r; time.sleep(1)
    return robots[b].can_fetch(UA,u)
def jsonld(html):
    out=[]
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>',html,re.S):
        try:j=json.loads(m.group(1))
        except: continue
        st=[j]
        while st:
            x=st.pop()
            if isinstance(x,list): st+=x
            elif isinstance(x,dict):
                if '@graph' in x: st+=x['@graph']
                t=x.get('@type'); 
                if t=='Recipe' or (isinstance(t,list) and 'Recipe' in t): out.append(x)
    return out
def get(dish,u):
    if not allowed(u): return dict(dish=dish,url=u,status='ROBOTS_BLOCKED')
    r=requests.get(u,headers={'User-Agent':UA},timeout=30); time.sleep(1.1)
    if r.status_code!=200: return dict(dish=dish,url=u,status=f'HTTP_{r.status_code}')
    rs=jsonld(r.text)
    if not rs: return dict(dish=dish,url=u,status='NO_JSONLD')
    x=rs[0]; y=x.get('recipeYield'); 
    return dict(dish=dish,url=u,status='OK',fetch_date=datetime.date.today().isoformat(),title=x.get('name'),yield_=json.dumps(y) if y is not None else '',ingredients=json.dumps(x.get('recipeIngredient',[]),ensure_ascii=False))
if __name__=='__main__':
    cand=[l.rstrip('\n').split('\t') for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
    res=[]
    for d,u in cand:
        try:r=get(d,u)
        except Exception as e:r=dict(dish=d,url=u,status='ERR '+str(e)[:60])
        print(r['status'],d,u,r.get('title'),r.get('yield_'),len(json.loads(r['ingredients'])) if r.get('ingredients') else '')
        res.append(r)
    json.dump(res,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
