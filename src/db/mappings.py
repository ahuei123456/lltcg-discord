# Character Name Mappings (English/Romaji -> Japanese Database Name)
CHARACTER_MAP = {
    # μ's
    "honoka": "高坂穂乃果",
    "kousaka honoka": "高坂穂乃果",
    "eli": "絢瀬絵里",
    "ayase eli": "絢瀬絵里",
    "kotori": "南ことり",
    "minami kotori": "南ことり",
    "umi": "園田海未",
    "sonoda umi": "園田海未",
    "rin": "星空凛",
    "hoshizora rin": "星空凛",
    "maki": "西木野真姫",
    "nishikino maki": "西木野真姫",
    "nozomi": "東條希",
    "tojo nozomi": "東條希",
    "hanayo": "小泉花陽",
    "koizumi hanayo": "小泉花陽",
    "nico": "矢澤にこ",
    "yazawa nico": "矢澤にこ",
    # Aqours
    "chika": "高海千歌",
    "takami chika": "高海千歌",
    "riko": "桜内梨子",
    "sakurauchi riko": "桜内梨子",
    "kanan": "松浦果南",
    "matsuura kanan": "松浦果南",
    "dia": "黒澤ダイヤ",
    "kurosawa dia": "黒澤ダイヤ",
    "you": "渡辺曜",
    "watanabe you": "渡辺曜",
    "yoshiko": "津島善子",
    "tsushima yoshiko": "津島善子",
    "yohane": "津島善子",
    "hanamaru": "国木田花丸",
    "kunikida hanamaru": "国木田花丸",
    "mari": "小原鞠莉",
    "ohara mari": "小原鞠莉",
    "ruby": "黒澤ルビィ",
    "kurosawa ruby": "黒澤ルビィ",
    # Nijigasaki
    "ayumu": "上原歩夢",
    "uehara ayumu": "上原歩夢",
    "kasumi": "中須かすみ",
    "nakasu kasumi": "中須かすみ",
    "shizuku": "桜坂しずく",
    "osaka shizuku": "桜坂しずく",
    "karin": "朝香果林",
    "asaka karin": "朝香果林",
    "ai": "宮下愛",
    "miyashita ai": "宮下愛",
    "kanata": "近江彼方",
    "konoe kanata": "近江彼方",
    "setsuna": "優木せつ菜",
    "yuki setsuna": "優木せつ菜",
    "emma": "エマ・ヴェルデ",
    "emma verde": "エマ・ヴェルデ",
    "rina": "天王寺璃奈",
    "tennoji rina": "天王寺璃奈",
    "shioriko": "三船栞子",
    "mifune shioriko": "三船栞子",
    "mia": "ミア・テイラー",
    "mia taylor": "ミア・テイラー",
    "lanzhu": "鐘嵐珠",
    "zhong lanzhu": "鐘嵐珠",
    # Liella!
    "kanon": "澁谷かのん",
    "shibuya kanon": "澁谷かのん",
    "keke": "唐可可",
    "tang keke": "唐可可",
    "chisato": "嵐千砂都",
    "arashi chisato": "嵐千砂都",
    "sumire": "平安名すみれ",
    "heanna sumire": "平安名すみれ",
    "ren": "葉月恋",
    "hazuki ren": "葉月恋",
    "kinako": "桜小路きな子",
    "sakurakoji kinako": "桜小路きな子",
    "mei": "米女メイ",
    "yoneme mei": "米女メイ",
    "shiki": "若菜四季",
    "wakana shiki": "若菜四季",
    "natsumi": "鬼塚夏美",
    "onitsuka natsumi": "鬼塚夏美",
    "margarete": "ウィーン・マルガレーテ",
    "wien margarete": "ウィーン・マルガレーテ",
    "tomari": "鬼塚冬毬",
    "onitsuka tomari": "鬼塚冬毬",
    # Hasunosora
    "kaho": "日野下花帆",
    "hinoshita kaho": "日野下花帆",
    "sayaka": "村野さやか",
    "murano sayaka": "村野さやか",
    "kozue": "乙宗梢",
    "otomune kozue": "乙宗梢",
    "tsuzuri": "夕霧綴理",
    "yugiri tsuzuri": "夕霧綴理",
    "rurino": "大沢瑠璃乃",
    "osawa rurino": "大沢瑠璃乃",
    "ruri": "大沢瑠璃乃",
    "megumi": "藤島慈",
    "fujishima megumi": "藤島慈",
    "ginko": "百生吟子",
    "momose ginko": "百生吟子",
    "kosuzu": "徒町小鈴",
    "kachimachi kosuzu": "徒町小鈴",
    "hime": "安養寺姫芽",
    "anyoji hime": "安養寺姫芽",
    "ceras": "セラス柳田リリエンフェルト",
    "ceras yanagida lilienfeld": "セラス柳田リリエンフェルト",
    "izumi": "桂城泉",
    "katsuragi izumi": "桂城泉",
}

# Group Name Mappings
GROUP_MAP = {
    "muse": "ラブライブ！",  # Usually mostly referred to as 'ラブライブ！' in earlier sets or 'μ's'? Need to check DB.
    # Checking card_data from user snippet: "ラブライブ！虹ヶ咲学園スクールアイドル同好会"
    "nijigasaki": "ラブライブ！虹ヶ咲学園スクールアイドル同好会",
    "aqours": "ラブライブ！サンシャイン!!",  # Assuming standard group naming convention in DB
    "liella": "ラブライブ！スーパースター!!",
    "hasunosora": "蓮ノ空女学院スクールアイドルクラブ",
    "mus": "ラブライブ！",
    "mu's": "ラブライブ！",
}

# Unit Name Mappings (English -> DB Value)
# Most units are in English/Latin usually, but we map lowercase to correct casing
UNIT_MAP = {
    # μ's
    "printemps": "Printemps",
    "lily white": "lily white",
    "bibi": "BiBi",
    # Aqours
    "cyaron": "CYaRon!",
    "cyaron!": "CYaRon!",
    "azalea": "AZALEA",
    "guilty kiss": "Guilty Kiss",
    # Nijigasaki
    "diverdiva": "DiverDiva",
    "azuna": "A・ZU・NA",
    "a・zu・na": "A・ZU・NA",
    "a.zu.na": "A・ZU・NA",
    "qu4rtz": "QU4RTZ",
    "quartz": "QU4RTZ",
    "r3birth": "R3BIRTH",
    "rebirth": "R3BIRTH",
    # Liella!
    "catchu": "CatChu!",
    "catchu!": "CatChu!",
    "kaleidoscore": "KALEIDOSCORE",
    "5yncri5e": "5yncri5e!",
    "5yncri5e!": "5yncri5e!",
    "syncrise": "5yncri5e!",
    # Hasunosora
    "cerise bouquet": "Cerise Bouquet",
    "dollchestra": "DOLLCHESTRA",
    "mira-cra park": "Mira-Cra Park!",
    "mira-cra park!": "Mira-Cra Park!",
    "miracra": "Mira-Cra Park!",
    "edel note": "Edel Note",  # Verify spelling
}

# Reverse Lookups for Autocomplete display (Code -> Human Readable)
# Since we map English input to Japanese DB value, for autocomplete we want to show:
# "Honoka (高坂穂乃果)"
REVERSE_CHAR_MAP = {}
for en, jp in CHARACTER_MAP.items():
    if jp not in REVERSE_CHAR_MAP:
        # Use key as label (capitalized)
        REVERSE_CHAR_MAP[jp] = en.title()
