import json,csv,statistics as st,collections,sys
sys.path.insert(0,'.')
import compute as c
recs={r['rid']:r for r in json.load(open('recipes_selected.json'))}
parsed=[]
for l in open('parsed_lines.txt'):
    if l.startswith('#') or not l.strip(): continue
    i,k,a,b,u,s=l.strip().split('|'); parsed.append((i,k,float(a),float(b),u,s))
raw={}
for rid,r in recs.items():
    for j,line in enumerate(json.loads(r['ingredients'])): raw[f"{rid}.{j+1:02d}"]=line
raw['R05.08']='[NOT in ingredient list; from method step 2: Heat 3 tablespoons of oil]'
assert set(raw)=={p[0] for p in parsed}, 'parse/raw mismatch'
byrec=collections.defaultdict(list)
for p in parsed: byrec[p[0].split('.')[0]].append(p)
CONDIMENT=c.SPICEKEYS|{'soy','honey','jaggery','kasuri','amchur','lemon_juice'}
res={}; qa={}
per_rows=[]; top10=[]
for rid in recs:
    res[rid]={}
    for sc in c.SCEN:
        o=c.run(recs,byrec[rid],sc); res[rid][sc]=c.summarize(o)
        if sc=='base':
            for r in o:
                per_rows.append(dict(rid=rid,dish=recs[rid]['dish'],url=recs[rid]['url'],line=raw[r['line_id'].split('/')[0]],line_id=r['line_id'],key=r['key'],qty=r['qty'],unit=r['unit'],status=r['status'],grams=None if r['grams'] is None else round(r['grams'],2),weight_basis=r['basis'],cofid_code=r['code'],**({} if not r['code'] else dict(cofid_name=c.cof_vals(r['code'])['name'],fat_100=c.cof_vals(r['code'])['F'],water_100=c.cof_vals(r['code'])['W'],kcal_100=round(c.cof_vals(r['code'])['KC'],1),fat_g=round(c.cof_vals(r['code'])['F']*r['grams']/100,3),water_g=round(c.cof_vals(r['code'])['W']*r['grams']/100,3),kcal=round(c.cof_vals(r['code'])['KC']*r['grams']/100,2),kcal_flag=c.cof_vals(r['code'])['flag']))))
            q=[r for r in o if r['status'] in('QUANTIFIED','QUANTIFIED_UNMAPPED')]
            mass=sum(r['grams'] for r in q)
            tests={}
            big=[r for r in q if r['key'] in CONDIMENT and r['grams']>30]
            tests['no_spice_condiment_gt_30g']=(not big, [(r['line_id'],r['key'],round(r['grams'])) for r in big])
            tests['mass_200_5000']=(200<=mass<=5000, round(mass))
            dflt=[r['line_id'] for r in q if abs(r['grams']-100)<1e-9 and r['basis']!='STATED']
            nobasis=[r['line_id'] for r in q if not r['basis']]
            tests['no_silent_100g_default']=(not nobasis,{'lines_without_explicit_rule':nobasis,'exactly_100g_but_from_documented_rule':dflt})
            mains=[r for r in q if r['key'] in('chicken_avg','chicken_dark','chicken_breast','chicken_leg_bone','prawn','spinach','okra','basmati','brown_basmati','toor') and r['unit'] in('g','kg','lb')]
            tests['main_ingredient_grams_match_line']=(all(abs(r['grams']-{'g':1,'kg':1000,'lb':453.6}[r['unit']]*r['qty'])<1e-6 for r in mains),[(r['line_id'],r['key'],round(r['grams'])) for r in mains])
            qa[rid]=dict(tests={k:{'pass':bool(v[0]),'detail':v[1]} for k,v in tests.items()},mass=mass)
            t10=sorted(q,key=lambda r:-r['grams'])[:10]
            top10.append(f"### {rid} {recs[rid]['dish']} | {recs[rid]['title']} | mass {mass:.0f} g\n"+'\n'.join(f"  {r['line_id']:9s} {r['key']:16s} {r['grams']:8.1f} g [{r['basis']}]  <- {raw[r['line_id'].split('/')[0]][:60]}" for r in t10))
keys=sorted({k for r in per_rows for k in r}); 
w=csv.DictWriter(open('per_ingredient.csv','w',newline=''),fieldnames=['rid','dish','url','line_id','line','key','qty','unit','status','grams','weight_basis','cofid_code','cofid_name','fat_100','water_100','kcal_100','fat_g','water_g','kcal','kcal_flag']); w.writeheader(); w.writerows(per_rows)
open('sanity_top10.txt','w').write('\n\n'.join(top10))
json.dump(dict(res=res,qa=qa),open('recipe_results_raw.json','w'),indent=1)
print('recipes',len(recs))
for rid in recs:
    b=res[rid]['base']; t=qa[rid]['tests']
    print(rid,recs[rid]['dish'][:18].ljust(18),f"mass {b['mass']:.0f} fat {b['fat']:.1f} M1 {b['M1']:.2f} M2 {b['M2']:.1f} unm {100*b['unmapped_share']:.1f}% kcalest {100*b['kcal_est_share']:.1f}%", 'FAIL:'+','.join(k for k,v in t.items() if not v['pass']) if not all(v['pass'] for v in t.values()) else 'sanity ok')
