import json,csv,math,statistics as st,sys
rows=json.load(open('cofid_proximates.json'))
COF={r[0]:r for r in rows}
def num(x,tr0=True):
    if x is None: return None
    s=str(x).strip()
    if s=='Tr': return 0.0 if tr0 else None
    try: return float(s)
    except: return None   # 'N' etc
# key -> dict(code, tsp_g|dens, cup_g, unit weights {unit:(g,basis)}, proxy note)
H='HANDOFF'; U='UNITS_XLSX'; A='ASSUMED'
def spice(code,**kw): d=dict(code=code,tsp=(2.5,H)); d.update(kw); return d
K={
'spinach':dict(code='13-572',cup=(30,U)),
'oil':dict(code='17-686',dens=(0.92,H),note='mustard/neutral oil -> CoFID oil, vegetable average'),
'sesame_oil':dict(code='17-043',dens=(0.92,H)),
'ghee':dict(code='17-640',dens=(0.91,H)),
'butter_unsalted':dict(code='17-661',dens=(0.91,H)),'butter_salted':dict(code='17-685',dens=(0.91,H)),
'cumin':spice('13-889'),'turmeric':spice('13-861'),'coriander_pd':spice('13-875'),'chilli_pd':spice('13-873'),
'dried_chilli':spice('13-873',piece=(3.33,U)),'garam':spice('13-829'),'curry_powder':spice('13-876'),
'sambar_powder':spice('13-876',note='PROXY: sambar powder -> curry powder'),
'asafoetida':spice('13-803'),'mustard_seed':spice('13-839'),'fennel':spice('13-827'),
'fenugreek_seed':spice('13-828',seed=(0.01,A)),'cardamom':spice('13-809',piece=(0.625,U)),
'cinnamon':spice('13-874',inch=(1.25,U)),'clove':spice('13-816',piece=(0.625,U)),'bay':spice('13-806',piece=(0.4,U)),
'pepper_black':spice('13-880',seed=(0.05,A)),'mace':spice('13-834',piece=(0.2,A)),'caraway':spice('13-808',note='PROXY: shahi jeera -> caraway'),
'saffron':spice('13-852',strand=(0.02,A)),
'salt':dict(code='17-367',tsp=(6,H)),'sugar':dict(code='17-063',tsp=(4.2,H)),
'jaggery':dict(code='17-060',tsp=(4.2,H),note='PROXY: jaggery -> sugar, brown'),'honey':dict(code='17-050',tsp=(5,U)),
'coriander_leaf':dict(code='13-888',cup=(16,U),sprig=(2,A),handful=(10,A)),
'mint':dict(code='13-836',cup=(16,U),bunch=(20,A)),
'curry_leaf':dict(code='13-821',sprig=(1,A),leaf=(0.2,A)),
'methi_leaf':dict(code='13-243',cup=(30,A),bunch=(150,A)),
'besan':dict(code='11-896',cup=(92,U)),'lemon_juice':dict(code='14-277',dens=(1.0,H)),
'potato':dict(code='13-489',piece=(70,U),cup=(150,A)),
'tomato':dict(code='13-517',piece=(50,U),cup=(180,U)),
'passata':dict(code='13-530',cup=(245,U)),'tomato_paste':dict(code='13-531',dens=(1.0,A)),
'okra':dict(code='13-300'),
'chicken_avg':dict(code='18-488'),'chicken_dark':dict(code='18-289',note='bone-in thighs: weight incl. bone, CoFID meat-only row (overstates edible meat)'),
'chicken_leg_bone':dict(code='18-294',note='CoFID leg quarter with skin weighed with bone'),'chicken_breast':dict(code='18-290'),
'yogurt':dict(code='12-184',dens=(1.03,H)),'yogurt_greek':dict(code='12-555',dens=(1.03,H)),
'cream_whipping':dict(code='12-333',dens=(1.0,H)),'cream_single':dict(code='12-332',dens=(1.0,H),note='Indian fresh cream (~25% fat) -> nearest CoFID single cream 19%'),
'milk':dict(code='12-596',dens=(1.03,H)),
'cashew':dict(code='14-811',piece=(1.5,H),cup=(137,U)),'coconut_fresh':dict(code='14-816',cup=(80,U)),
'basmati':dict(code='11-857',cup=(160,U)),'brown_basmati':dict(code='11-866',cup=(160,U)),
'toor':dict(code='13-104',cup=(175,U)),'chana_dal':dict(code='13-076',cup=(200,U)),'urad':dict(code='13-060',cup=(175,U)),
'tamarind':dict(code='13-856',tsp=(3.33,U)),'drumstick':dict(code='13-238',piece=(40,A)),
'carrot':dict(code='13-496',piece=(60,U),cup=(128,U)),'green_bean':dict(code='13-514',piece=(3.85,U),cup=(100,U)),
'peas':dict(code='13-527',cup=(134,U)),'cauliflower':dict(code='13-512',cup=(100,A)),
'brinjal':dict(code='13-161',piece=(80,A)),'pumpkin':dict(code='13-326',cup=(120,A)),
'prawn':dict(code='16-387'),'prawn_cooked':dict(code='16-389',piece=(12,A)),
'bell_green':dict(code='13-318',piece=(50,U),cup=(149,U)),'bell_red':dict(code='13-524',piece=(50,U)),
'babycorn':dict(code='13-634',cup=(100,A),note='boiled baby corn row used for raw'),
'soy':dict(code='17-721',dens=(1.0,A)),
'mixveg':dict(code='13-514',cup=(100,U),note='PROXY: unspecified mixed vegetables -> green beans'),
'onion':dict(code='13-499',piece=(60,U),large=(90,A),small=(45,A),cup=(160,U)),
'shallot':dict(code='13-342',piece=(15,A)),'fried_onion':dict(code='13-591',tsp=(1.67,A)),
'garlic':dict(code='13-244',clove=(0.625,U),tsp=(2.8,U)),
'ginger':dict(code='13-890',inch=(12.66,U),cup=(96,U)),
'green_chilli':dict(code='13-316',piece=(3.33,U),tsp=(3,A)),
'garlic_paste':dict(code='13-244',dens=(1.0,A)),'ginger_paste':dict(code='13-890',dens=(1.0,A)),
# unmapped (no CoFID/INDB row; mass reported as excluded)
'kasuri':dict(code=None,tsp=(0.7,A)),'amchur':dict(code=None,tsp=(2.5,H)),'star_anise':dict(code=None,piece=(0.5,A)),
'stone_flower':dict(code=None,piece=(0.5,A)),'ajwain':dict(code=None,tsp=(2.5,H)),
}
SPICEKEYS={k for k,v in K.items() if 'tsp' in v and v['tsp'][0] in (2.5,6,4.2,0.7)} - {'sugar','jaggery'}|{'salt'}
def grams(key,unit,q,cup_ml=240,vegx=1.0):
    d=K[key]; 
    if unit=='g': return q,'STATED'
    if unit=='kg': return 1000*q,'STATED'
    if unit=='lb': return 453.6*q,'STATED'
    if unit=='ml':
        return q*d['dens'][0],'STATED' if 'dens' in d else None
    if unit=='pinch': return 0.3*q,H
    def tsp_g():
        if 'tsp' in d: return d['tsp']
        if 'dens' in d: return (5*d['dens'][0],d['dens'][1])
        if 'cup' in d: return (d['cup'][0]/48,d['cup'][1])
        raise KeyError((key,unit))
    if unit=='tsp': g,b=tsp_g(); return q*g,b
    if unit=='tbsp': g,b=tsp_g(); return q*3*g,b
    if unit=='cup':
        if 'cup' in d: return q*d['cup'][0]*cup_ml/240,d['cup'][1]
        if 'dens' in d: return q*cup_ml*d['dens'][0],d['dens'][1]
        raise KeyError((key,unit))
    if unit in d:
        g,b=d[unit]; 
        if unit in('piece','large','small') and key in VEGKEYS: g*=vegx
        return q*g,b
    raise KeyError((key,unit))
VEGKEYS={'onion','potato','tomato','carrot','bell_green','bell_red','brinjal'}
def cof_vals(code):
    r=COF[code]
    W,P,F,C,KC=num(r[7]),num(r[9]),num(r[10]),num(r[11]),num(r[12])
    flag=''
    if KC is None:
        Cc=C if C is not None else max(0,100-(W or 0)-(P or 0)-(F or 0)-6)  # ash assumed 6 g
        KC=4*(P or 0)+9*(F or 0)+4*Cc; flag='KCAL_ATWATER_ESTIMATE'
    return dict(name=r[1],W=W or 0.0,P=P or 0.0,F=F or 0.0,C=C,KC=KC,flag=flag)
SCEN={'base':{},'oil_asreq_1tbsp':dict(oil=True),'cup200':dict(cup_ml=200),'min_qty':dict(qsel='min'),'max_qty':dict(qsel='max'),'veg_pieces_x1.5':dict(vegx=1.5)}
def run(recipes,parsed,scen):
    o=SCEN[scen]; out=[]
    for pl in parsed:
        rid,key,qmin,qmax,unit,status=pl
        q=(qmin+qmax)/2
        if o.get('qsel')=='min': q=qmin
        if o.get('qsel')=='max': q=qmax
        rec=dict(line_id=f"{rid}",rid=rid.split('.')[0],key=key,unit=unit,qmin=qmin,qmax=qmax,qty=q,status=status,grams=None,basis='',code=None)
        if status in('W','SIDE'):
            rec['status']={'W':'EXCLUDED_WATER','SIDE':'EXCLUDED_SIDE_DISH'}[status]
        elif status=='NQ':
            rec['status']='NOT_QUANTIFIED'
        elif status in('NQOIL','FRY'):
            if o.get('oil'):
                g,b=grams('oil','tbsp',1,); rec.update(status='QUANTIFIED',grams=g,basis='ASSUMED_1TBSP_AS_REQUIRED',key='oil',code=K['oil']['code'])
            else: rec['status']='NOT_QUANTIFIED'
        else:
            if key in('ginger_garlic',):
                g,b=grams('garlic_paste' ,unit,q,o.get('cup_ml',240),o.get('vegx',1.0)) ; g/=2
                for sub in('ginger','garlic'):
                    r2=dict(rec); r2.update(key=sub,grams=g,basis=b,status='QUANTIFIED',code=K[sub]['code'],line_id=rec['line_id']+'/'+sub); out.append(r2)
                continue
            g,b=grams(key,unit,q,o.get('cup_ml',240),o.get('vegx',1.0))
            rec.update(grams=g,basis=b,status='QUANTIFIED',code=K[key]['code'])
            if K[key]['code'] is None: rec['status']='QUANTIFIED_UNMAPPED'
        out.append(rec)
    return out
def summarize(rows_):
    F=Wt=Mass=KC=0.0;unm=0.0;mapped=0.0;kcest=0.0
    for r in rows_:
        if r['status']!='QUANTIFIED': 
            if r['status']=='QUANTIFIED_UNMAPPED': unm+=r['grams']
            continue
        v=cof_vals(r['code']); g=r['grams']/100
        F+=v['F']*g; Wt+=v['W']*g; Mass+=r['grams']; KC+=v['KC']*g; mapped+=r['grams']
        if v['flag']: kcest+=v['KC']*g
    dm=Mass-Wt
    return dict(fat=F,water=Wt,mass=Mass,kcal=KC,dm=dm,M1=100*F/dm if dm>0 else None,M2=100*9*F/KC if KC>0 else None,
                unmapped_g=unm,unmapped_share=unm/(unm+mapped) if unm+mapped else 0,kcal_est_share=kcest/KC if KC else 0,
                M3_60=100*F/dm*0.40 if dm>0 else None,M3_80=100*F/dm*0.20 if dm>0 else None)
