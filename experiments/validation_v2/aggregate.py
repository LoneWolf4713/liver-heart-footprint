import json,csv,statistics as st,collections
R=json.load(open('recipe_results_raw.json')); res=R['res']; qa=R['qa']
recs={r['rid']:r for r in json.load(open('recipes_selected.json'))}
EXCL={'R27':'depends on 3x70 ml of an unspecified "curry broth" base sauce with no composition; excluded (only 232 g of quantified ingredients)'}
gt=list(csv.DictReader(open('ground_truth.csv')))
USE=[('saag','15-629'),('methi aloo','15-628'),('bhindi sabzi','15-627'),('sambar','12-467'),('vegetable pilau','12-472'),
     ('chicken biryani','19-454'),('prawn bhuna','16-365'),('chicken tikka masala','19-296'),('chicken tikka masala','p.14 Table 5'),
     ('chicken korma','p.14 Table 5'),('chicken jalfrezi','p.14 Table 5')]
def f(x): 
    try: return float(x)
    except: return None
out=[]
for dish,code in USE:
    g=[r for r in gt if r['dish']==dish and r['code']==code][0]
    fat,water,kc=f(g['fat']),f(g['water']),f(g['energy_kcal'])
    lab=dict(fat100=fat,water100=water,kcal100=kc,M2=100*9*fat/kc,M1=(100*fat/(100-water) if water is not None else None),
             M3=fat)
    rids=[r for r in recs if recs[r]['dish']==dish and r not in EXCL]
    def vals(scs,m): return [res[r][s][m] for r in rids for s in scs]
    d=dict(dish=dish,gt_source=g['source'],gt_code=code,gt_name=g['name'],setting=g['setting'],lab=lab,recipes=rids,n_recipes=len(rids),
           recipe_urls=[recs[r]['url'] for r in rids],sanity_all_pass=all(all(t['pass'] for t in qa[r]['tests'].values()) for r in rids),
           mass_unmapped_share_max=max(res[r]['base']['unmapped_share'] for r in rids))
    for m in('M1','M2'):
        if lab[m] is None: d[m]=None; continue
        base=vals(['base'],m); prim=vals(['base','oil_asreq_1tbsp'],m); wide=vals(list(res[rids[0]].keys()),m)
        med=st.median(base)
        d[m]=dict(lab=lab[m],base_by_recipe=dict(zip(rids,[round(x,2) for x in base])),median_base=med,ratio_median_over_lab=med/lab[m],
                  range_primary=[min(prim),max(prim)],inside_primary=min(prim)<=lab[m]<=max(prim),
                  range_wide=[min(wide),max(wide)],inside_wide=min(wide)<=lab[m]<=max(wide),
                  inside_base_only=min(base)<=lab[m]<=max(base))
    # M3 reference: fat per 100g as eaten, moisture 60-80%
    m3=[res[r]['base']['M3_60'] for r in rids]+[res[r]['base']['M3_80'] for r in rids]
    d['M3']=dict(lab_fat_per_100g=fat,recipe_band=[min(m3),max(m3)],inside=min(m3)<=fat<=max(m3),note='fat per 100 g of dish at assumed final moisture 60-80%; reference only')
    out.append(d)
def summ(items,m):
    it=[d for d in items if d[m]]
    if not it: return None
    return dict(n_dishes=len(it),inside_primary=sum(d[m]['inside_primary'] for d in it),inside_wide=sum(d[m]['inside_wide'] for d in it),
                inside_base_only=sum(d[m]['inside_base_only'] for d in it),
                median_ratio=st.median([d[m]['ratio_median_over_lab'] for d in it]),
                ratios={d['dish']+('*' if d['gt_code'].startswith('p.') else ''):round(d[m]['ratio_median_over_lab'],2) for d in it})
groups={'all':out,'home':[d for d in out if d['setting']=='home'],'takeaway':[d for d in out if d['setting']=='takeaway'],'retail':[d for d in out if d['setting']=='retail']}
overall={g:{m:summ(v,m) for m in('M1','M2')} for g,v in groups.items()}
qa_sum=dict(recipes_used=sorted(r for r in recs if r not in EXCL),recipes_excluded=EXCL,
   sanity={r:{k:v['pass'] for k,v in qa[r]['tests'].items()} for r in recs},
   unmapped_share={r:round(res[r]['base']['unmapped_share'],4) for r in recs},
   kcal_atwater_estimate_share={r:round(res[r]['base']['kcal_est_share'],3) for r in recs})
json.dump(dict(dishes=out,overall=overall,qa=qa_sum,recipe_results=res),open('results.json','w'),indent=1,default=str)
for d in out:
    print(d['dish'].ljust(22),d['setting'].ljust(9),d['gt_code'].ljust(13),'n',d['n_recipes'],end=' | ')
    for m in('M1','M2'):
        if d[m]: x=d[m]; print(m,f"lab {x['lab']:.1f} med {x['median_base']:.1f} rng {x['range_primary'][0]:.1f}-{x['range_primary'][1]:.1f} in:{x['inside_primary']} r={x['ratio_median_over_lab']:.2f}",end=' | ')
    print()
for g,v in overall.items(): print(g,{m:(None if not s else (s['n_dishes'],s['inside_primary'],round(s['median_ratio'],2))) for m,s in v.items()})
