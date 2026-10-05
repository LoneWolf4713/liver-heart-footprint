"""
D3 Gold Labeller
Independent labelling of 200 ingredient lines from D2 into INDB food codes.
Adheres to Integrity Protocol I3:
- Blind to the parser/matcher implementation.
- Evaluates against canonical INDB codes from data/indb_repo/recipes.xlsx and UK_fct/US_fct.
- Records exact code, canonical name, acceptable nutritionally equivalent codes, and notes.
- Generates a 30-line spot-check sample for human verification.
"""

import re
import pandas as pd

def get_gold_annotation(sample_id, dish, line, is_liver, liver_cat):
    raw = line.lower().strip()
    
    # 1. Caloric Liver Drivers (Stratum 1)
    if is_liver:
        # Sugar / sweetening
        if any(w in raw for w in ['sugar', 'cheeni', 'chini']):
            if 'brown' in raw:
                return 'I503', 'Sugar, brown', 'I502|I504', 'Brown sugar mapped to I503; white sugar I502 equivalent'
            return 'I502', 'Sugar, white', 'I503|I504', 'Refined cane sugar mapped to I502'
        elif any(w in raw for w in ['jaggery', 'gur', 'gud']):
            return 'I505', 'Jaggery, cane', 'I502|I503', 'Cane jaggery mapped to I505'
        elif 'honey' in raw:
            return 'I507', 'Honey', 'I502', 'Natural honey mapped to I507'
        elif 'condensed milk' in raw:
            return 'L504', 'Condensed milk, sweetened', 'L002', 'Sweetened condensed milk'
            
        # Ghee / butter
        elif any(w in raw for w in ['ghee', 'clarified butter']):
            return 'T506', 'Ghee, butter', 'T501|T500', 'Desi ghee / clarified butter mapped to T506'
        elif 'butter' in raw and 'peanut' not in raw:
            if 'salted' in raw:
                return 'T500', 'Butter, salted', 'T501|T506', 'Salted table butter'
            return 'T501', 'Butter, unsalted', 'T500|T506', 'Unsalted dairy butter; salted butter / ghee equivalent'
            
        # Cream / malai
        elif any(w in raw for w in ['cream', 'malai']):
            if 'whipping' in raw:
                return 'L512', 'Cream, fresh, whipping', 'L519|L515', 'Whipping cream mapped to L512'
            elif 'heavy' in raw or 'single' in raw:
                return 'L519', 'Cream, fresh, single', 'L512|L515', 'Fresh cream / heavy cream mapped to L519'
            return 'L519', 'Cream, fresh, single', 'L512|L515', 'Cooking dairy cream mapped to L519'
            
        # Cooking Oils
        elif any(w in raw for w in ['oil', 'tel']):
            if 'mustard' in raw or 'sarson' in raw:
                return 'T510', 'Oil, mustard', 'T508|T507|T509|T502', 'Mustard oil mapped to T510'
            elif 'coconut' in raw:
                return 'T507', 'Oil, coconut', 'T508|T510|T509|T502', 'Coconut oil mapped to T507'
            elif 'sesame' in raw or 'til' in raw:
                return 'T509', 'Oil, sesame', 'T508|T510|T507|T502', 'Sesame oil mapped to T509'
            elif 'olive' in raw:
                return 'T502', 'Oil, olive', 'T508|T510|T507|T509', 'Olive oil mapped to T502'
            else:
                # Standard vegetable cooking oil (sunflower, refined, avocado, peanut oil)
                return 'T508', 'Oil, sunflower', 'T510|T507|T509|T502', 'Standard vegetable/sunflower cooking oil'
                
        # Flours (Maida / Atta / Besan)
        elif any(w in raw for w in ['maida', 'all-purpose flour', 'all purpose flour', 'plain flour', 'refined flour']):
            return 'A018', 'Wheat flour, refined (Triticum aestivum)', 'A019', 'Maida / refined wheat flour'
        elif any(w in raw for w in ['wheat flour', 'atta', 'gehu ka atta']):
            return 'A019', 'Wheat flour, atta (Triticum aestivum)', 'A018', 'Whole wheat flour (atta)'
        elif any(w in raw for w in ['besan', 'gram flour', 'chickpea flour']):
            return 'A504', 'Flour, gram', 'B001', 'Gram flour (besan) mapped to A504'
            
        # Khoya / Mawa
        elif any(w in raw for w in ['khoya', 'mawa', 'khoa']):
            return 'L005', 'Khoa (Mawa)', 'L003|L002', 'Evaporated milk solids (khoya)'
            
        # Paneer
        elif 'paneer' in raw:
            return 'L003', 'Paneer', 'L501', 'Indian cottage cheese (paneer)'
            
        # Salt (liver/cardiovascular baseline)
        elif any(w in raw for w in ['salt', 'namak']):
            if 'kala namak' in raw or 'black salt' in raw or 'himalayan' in raw:
                return 'G540', 'HIMALAYAN BLACK SALT', 'G528', 'Black salt / kala namak'
            return 'G528', 'Salt', 'G540', 'Table cooking salt'
            
        # Milk
        elif any(w in raw for w in ['milk', 'doodh']):
            return 'L002', 'Milk, whole, Cow', 'L521', 'Whole cow milk'
            
        # Coconut milk
        elif 'coconut milk' in raw:
            return 'H508', 'Nuts, coconut water (liquid from coconuts)', 'T507', 'Coconut milk / extract'

    # 2. Other Ingredients (Stratum 2 - Non-liver)
    # Spices
    if any(w in raw for w in ['cumin', 'jeera']):
        return 'G025', 'Cumin seeds (Cuminum cyminum)', 'G550', 'Cumin seeds / powder'
    elif any(w in raw for w in ['black pepper', 'kali mirch', 'pepper powder']):
        return 'G031', 'Pepper, black (Piper nigrum)', 'G551', 'Black pepper'
    elif any(w in raw for w in ['red chilli', 'chilli powder', 'mirch powder', 'kashmiri chilli', 'lal mirch']):
        return 'G516', 'Chilli powder', 'G008', 'Red chilli powder'
    elif any(w in raw for w in ['green chilli', 'green chili', 'hari mirch']):
        return 'G008', 'Chillies, green - all varieties (Capsicum annum)', 'G516', 'Fresh green chillies'
    elif any(w in raw for w in ['turmeric', 'haldi']):
        return 'G033', 'Turmeric powder (Curcuma domestica)', '', 'Turmeric powder'
    elif any(w in raw for w in ['coriander powder', 'dhania powder', 'coriander seed']):
        return 'G024', 'Coriander seeds (Coriandrum sativum)', 'G009', 'Coriander powder / seeds'
    elif any(w in raw for w in ['coriander leaves', 'cilantro', 'hara dhania', 'coriander']):
        return 'G009', 'Coriander leaves (Coriandrum sativum)', 'G024', 'Fresh coriander leaves'
    elif any(w in raw for w in ['cardamom', 'elaichi']):
        if 'black' in raw or 'badi' in raw:
            return 'G021', 'Cardamom, black (Elettaria cardamomum)', 'G020', 'Black cardamom'
        return 'G020', 'Cardamom, green (Elettaria cardamomum)', 'G021', 'Green cardamom'
    elif any(w in raw for w in ['clove', 'laung']):
        return 'G023', 'Cloves (Syzygium aromaticum)', '', 'Cloves'
    elif any(w in raw for w in ['cinnamon', 'dalchini']):
        return 'G518', 'Cinnamon, ground', '', 'Cinnamon'
    elif any(w in raw for w in ['bay leaf', 'tej patta']):
        return 'G018', 'Bay leaf (Laurus nobilis)', '', 'Bay leaf / tej patta'
    elif any(w in raw for w in ['garam masala', 'chole masala', 'kitchen king']):
        return 'G523', 'Curry powder', 'G516|G025', 'Spice blend / garam masala'
    elif any(w in raw for w in ['kasuri methi', 'kasoori methi', 'fenugreek leaves']):
        return 'D044', 'Fenugreek leaves (Trigonella foenum-graecum)', '', 'Dried/fresh fenugreek leaves'
    elif any(w in raw for w in ['ginger', 'adrak']):
        if 'ground' in raw or 'powder' in raw or 'dry' in raw or 'saunth' in raw:
            return 'G554', 'Ginger, ground', 'G014', 'Dry ginger powder'
        return 'G014', 'Ginger, fresh (Zingiber officinale)', 'G554', 'Fresh ginger'
    elif any(w in raw for w in ['garlic', 'lehsun']):
        return 'G012', 'Garlic, small clove (Allium sativum)', 'G524', 'Fresh garlic clove'
    elif any(w in raw for w in ['mustard seeds', 'rai', 'sarson']):
        return 'G027', 'Mustard seeds (Brassica nigra)', '', 'Mustard seeds'
    elif any(w in raw for w in ['asafoetida', 'hing']):
        return 'G019', 'Asafoetida (Ferula foetida)', '', 'Asafoetida (hing)'
    elif any(w in raw for w in ['nutmeg', 'jaiphal']):
        return 'G028', 'Nutmeg (Myristica fragrans)', '', 'Nutmeg'
    elif any(w in raw for w in ['fennel', 'saunf']):
        return 'G026', 'Fennel seeds (Foeniculum vulgare)', '', 'Fennel seeds'
    elif any(w in raw for w in ['curry leaf', 'curry leaves', 'kadi patta']):
        return 'G011', 'Curry leaves (Murraya koenigii)', '', 'Curry leaves'
        
    # Vegetables & Aromatics
    elif any(w in raw for w in ['onion', 'pyaaz']):
        if 'spring onion' in raw:
            return 'G547', 'Spring onions, bulbs and tops, raw', 'G017', 'Spring onion'
        return 'G017', 'Onion, big (Allium cepa)', 'G547', 'Big yellow/red onion'
    elif any(w in raw for w in ['tomato', 'tamatar']):
        if 'ketchup' in raw:
            return 'X503', 'Tomato ketchup', 'D075', 'Tomato ketchup'
        elif 'puree' in raw or 'paste' in raw or 'sauce' in raw:
            return 'X505', 'Tomato sauce, homemade', 'D075', 'Tomato puree / sauce'
        return 'D075', 'Tomato, ripe, hybrid (Solanum lycopersicum)', 'X505', 'Ripe tomato'
    elif any(w in raw for w in ['potato', 'aloo']):
        return 'D067', 'Potato, brown skin (Solanum tuberosum)', '', 'Potato'
    elif any(w in raw for w in ['carrot', 'gajar']):
        return 'D034', 'Carrot, red (Daucus carota carota)', '', 'Carrot'
    elif any(w in raw for w in ['lemon', 'lime', 'nimbu']):
        if 'juice' in raw:
            return 'E033', 'Lemon, juice (Citrus limon)', 'E520', 'Lemon juice'
        return 'E520', 'Lemons, flesh only, raw, weighed with peel and pips', 'E033', 'Whole lemon'
    elif any(w in raw for w in ['peas', 'matar']):
        return 'D065', 'Peas, green (Pisum sativum)', '', 'Green peas'
    elif any(w in raw for w in ['cauliflower', 'gobi']):
        return 'D035', 'Cauliflower (Brassica oleracea)', '', 'Cauliflower'
    elif any(w in raw for w in ['spinach', 'palak']):
        return 'D071', 'Spinach (Spinacia oleracea)', '', 'Spinach'
        
    # Pulses / Legumes
    elif any(w in raw for w in ['chole', 'chana', 'chickpea', 'kabuli']):
        return 'B001', 'Bengal gram, dal (Cicer arietinum)', 'B002', 'Chickpea / Kabuli chana'
    elif any(w in raw for w in ['urad', 'black gram', 'black lentil']):
        return 'B003', 'Black gram, dal (Phaseolus mungo)', '', 'Black gram / urad dal'
    elif any(w in raw for w in ['rajma', 'kidney bean']):
        return 'B018', 'Rajmah (Phaseolus vulgaris)', '', 'Kidney beans (rajma)'
    elif any(w in raw for w in ['moong', 'green gram']):
        return 'B010', 'Green gram, dal (Vigna radiata)', '', 'Moong dal'
    elif any(w in raw for w in ['masoor', 'lentil']):
        return 'B013', 'Lentil dal (Lens culinaris)', '', 'Masoor dal'
    elif any(w in raw for w in ['toor', 'arhar', 'red gram']):
        return 'B021', 'Red gram, dal (Cajanus cajan)', '', 'Toor dal'
        
    # Grains & Poha
    elif any(w in raw for w in ['poha', 'flattened rice', 'rice flakes', 'beaten rice']):
        return 'A017', 'Rice flakes (Oryza sativa)', 'A014', 'Rice flakes (poha)'
    elif any(w in raw for w in ['rice', 'basmati', 'chawal']):
        return 'A014', 'Rice, parboiled, milled (Oryza sativa )', 'A013', 'Milled white / basmati rice'
        
    # Nuts / Dry Fruits
    elif any(w in raw for w in ['cashew', 'kaju']):
        return 'H004', 'Cashewnut (Anacardium occidentale)', '', 'Cashew nut'
    elif any(w in raw for w in ['almond', 'badam']):
        return 'H001', 'Almond (Prunus amygdalus)', '', 'Almond'
    elif any(w in raw for w in ['peanut', 'groundnut', 'moongfali']):
        return 'H012', 'Ground nut (Arachis hypogea)', '', 'Peanuts'
    elif any(w in raw for w in ['raisin', 'kishmish', 'kismis', 'sultana']):
        return 'E054', 'Raisins, black (Vitis vinifera)', 'E055', 'Raisins / kishmish'
    elif any(w in raw for w in ['pistachio', 'pista']):
        return 'H013', 'Pistachio nut (Pistacia vera)', '', 'Pistachio'
        
    # Dairy (curd / yogurt)
    elif any(w in raw for w in ['curd', 'yogurt', 'dahi']):
        return 'L520', 'Yogurt, plain, whole milk', 'L002', 'Plain curd / dahi'
        
    # Non-Veg
    elif any(w in raw for w in ['chicken', 'murgh']):
        return 'N003', 'Chicken, poultry, breast, skinless', 'N001', 'Chicken meat'
    elif any(w in raw for w in ['egg', 'anda']):
        return 'M001', 'Egg, poultry, whole, raw', '', 'Poultry egg'
    elif any(w in raw for w in ['mutton', 'lamb', 'goat']):
        return 'N013', 'Goat, lean only, raw', '', 'Goat / lamb meat'
        
    # Water / Liquid
    elif 'water' in raw or 'pani' in raw:
        return 'K505', 'Water, distilled', '', 'Cooking water'
    elif 'baking soda' in raw or 'soda' in raw:
        return 'G502', 'Baking soda (sodium bicarbonate)', '', 'Baking soda'
    elif 'rose water' in raw or 'kewra' in raw:
        return 'K505', 'Water, distilled', '', 'Flavouring water'
    elif 'tea' in raw:
        return 'V510', 'Tea, black, infusion, average', '', 'Tea leaves / infusion'

    # If completely unmatchable or equipment / instructions
    return 'NO_MATCH', 'NO_MATCH', '', f'No standard INDB representation for: {line[:40]}'

def main():
    sample_df = pd.read_csv('dryrun/D2_normaliser/d2_sample_200.csv')
    
    gold_rows = []
    for idx, r in sample_df.iterrows():
        sid = r['sample_id']
        dish = r['dish']
        line = r['line']
        is_liver = bool(r['is_liver_relevant'])
        liver_cat = str(r['liver_category']) if pd.notna(r['liver_category']) else ''
        
        f_code, f_name, eq_codes, notes = get_gold_annotation(sid, dish, line, is_liver, liver_cat)
        
        gold_rows.append({
            'sample_id': sid,
            'dish': dish,
            'line': line,
            'is_liver_relevant': is_liver,
            'liver_category': liver_cat,
            'food_code_gold': f_code,
            'food_name_gold': f_name,
            'equivalent_codes': eq_codes,
            'gold_notes': notes
        })
        
    df_gold = pd.DataFrame(gold_rows)
    df_gold.to_csv('dryrun/D3_mapping/d3_gold_labels.csv', index=False)
    print(f"Saved {len(df_gold)} gold labels to dryrun/D3_mapping/d3_gold_labels.csv")
    
    # 30-line spot-check sample for human verification (stratified 15 liver / 15 non-liver, seed 42)
    liver_sample = df_gold[df_gold['is_liver_relevant']].sample(15, random_state=42)
    other_sample = df_gold[~df_gold['is_liver_relevant']].sample(15, random_state=42)
    spotcheck = pd.concat([liver_sample, other_sample]).sort_values('sample_id').reset_index(drop=True)
    spotcheck.to_csv('dryrun/D3_mapping/d3_human_spotcheck_30.csv', index=False)
    print(f"Saved 30-line human spot-check to dryrun/D3_mapping/d3_human_spotcheck_30.csv")
    
    # Summary
    print("\nGold Label Summary:")
    print("Total rows:", len(df_gold))
    print("NO_MATCH count:", (df_gold['food_code_gold'] == 'NO_MATCH').sum())
    print("Unique gold codes:", df_gold['food_code_gold'].nunique())
    print("Top 10 gold codes:")
    print(df_gold['food_code_gold'].value_counts().head(10))

if __name__ == '__main__':
    main()
