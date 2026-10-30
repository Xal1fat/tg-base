# -*- coding: utf-8 -*-
"""Переводим служебные подписи шаблонов (заход, когда) и правим JS."""
import json, re

ANGLE_UA = {
1:"Оффер + портфоліо",2:"Спостереження: лише директ",3:"Аудит їхнього сайту",4:"Лише Instagram",
5:"Запит «після ремонту»",6:"Питання про Google",7:"Безкоштовний макет",8:"Невелика команда",
9:"Оффер + кейс у ніші",10:"Дорогий чек",11:"Калькулятор кошторисів",12:"Новобудови",
13:"Аудит їхнього сайту",14:"Питання про Google",15:"Безкоштовний макет",16:"Бригада / виконроб",
}
WHEN_UA = {
1:"Компанія з активним Instagram і без сайту",2:"Ціни та замовлення — лише в переписці",
3:"Сайт є, але без цін або без форми",4:"Уся робота в соцмережах, посилання веде в директ",
5:"Є прибирання після ремонту або хімчистка",6:"Лише соцмережі, сайту немає",
7:"Холодний контакт, довгий захід не спрацює",8:"Приватний клінер або мала бригада",
9:"Ремонт під ключ, є Instagram або OLX",10:"Середній чек вище 300 тис. грн",
11:"Багато вхідних «а скільки буде коштувати»",12:"Працюють по новобудовах, сезон здачі",
13:"Сайт є, але без фото обʼєктів, цін і форми",14:"Лише соцмережі та сарафан",
15:"Холодний контакт без зачіпки",16:"Невелика бригада без бренду",
}

html = open("index.html", encoding="utf-8").read()

m = re.search(r"const TEMPLATES = (\[.*?\]);", html, re.S)
assert m, "templates block not found"
tpls = json.loads(m.group(1))
for t in tpls:
    t["angleUa"] = ANGLE_UA[t["n"]]
    t["whenUa"] = WHEN_UA[t["n"]]
new = "const TEMPLATES = " + json.dumps(tpls, ensure_ascii=False, indent=1) + ";"
html = html[:m.start()] + new + html[m.end():]

# ---- JS: хелперы ----
old_helper = '''  function tplText(t, lang){
    return (lang === "ua" && t.textUa) ? t.textUa : t.text;
  }'''
new_helper = '''  function tplText(t, lang){
    return (lang === "ua" && t.textUa) ? t.textUa : t.text;
  }
  function tplAngle(t, lang){
    return (lang === "ua" && t.angleUa) ? t.angleUa : t.angle;
  }
  function tplWhen(t, lang){
    return (lang === "ua" && t.whenUa) ? t.whenUa : t.when;
  }'''
assert old_helper in html
html = html.replace(old_helper, new_helper)

# ---- JS: карточка шаблона ----
old_card = '''          <div><b>${t.n}. ${esc(t.angle)}</b><br><span>${esc(NICHES[t.niche].label)} · ${esc(t.when)}</span></div>'''
new_card = '''          <div><b>${t.n}. ${esc(tplAngle(t, lang))}</b><br><span>${esc(NICHES[t.niche].label)} · ${esc(tplWhen(t, lang))}</span></div>'''
assert old_card in html
html = html.replace(old_card, new_card)

# ---- JS: опции композера через функцию ----
old_opts = '''    $("#cTemplate").innerHTML = own.map(t=>`<option value="${t.n}"${t.n===n?" selected":""}>${t.n}. ${esc(t.angle)}</option>`).join("");
    $("#cTemplate").value = String(n);'''
new_opts = '''    renderComposerOptions(own, n);'''
assert old_opts in html
html = html.replace(old_opts, new_opts)

# добавляем функцию перед openComposer
anchor = '''  function openComposer(contactId, tplN){'''
fn = '''  function renderComposerOptions(own, n){
    const lang = composerCtx.lang || "ru";
    $("#cTemplate").innerHTML = own.map(t=>`<option value="${t.n}"${t.n===n?" selected":""}>${t.n}. ${esc(tplAngle(t, lang))}</option>`).join("");
    $("#cTemplate").value = String(n);
  }

  function openComposer(contactId, tplN){'''
assert anchor in html
html = html.replace(anchor, fn, 1)

# ---- JS: при переключении языка обновляем и опции ----
old_lang = '''        $("#cLangHint").textContent = composerCtx.lang === "ua" ? "текст українською" : "текст на русском";
        applyTemplate();'''
new_lang = '''        $("#cLangHint").textContent = composerCtx.lang === "ua" ? "текст українською" : "текст на русском";
        const cc = state.contacts.find(x=>x.id===composerCtx.contactId);
        if(cc) renderComposerOptions(TEMPLATES.filter(t=>t.niche===cc.niche), Number(composerCtx.tplN));
        applyTemplate();'''
assert old_lang in html
html = html.replace(old_lang, new_lang)

# ---- источник в UA-тексте ----
old_src = '''    const srcRu = (c.src && c.src.trim()) ? c.src.trim().toLowerCase() : "поиска";'''
new_src = '''    const srcRu = (c.src && c.src.trim()) ? c.src.trim().toLowerCase() : "поиска";
    let srcUaRaw = (c.src && c.src.trim()) ? c.src.trim().toLowerCase() : "пошуку";
    srcUaRaw = srcUaRaw.replace("перебор ников", "перебір ників").replace("поиск", "пошук").replace("поиска", "пошуку");'''
assert old_src in html
html = html.replace(old_src, new_src)

html = html.replace('''    const srcUa = (c.src && c.src.trim()) ? c.src.trim().toLowerCase() : "пошуку";''',
                    '''    const srcUa = srcUaRaw;''')

open("index.html", "w", encoding="utf-8").write(html)
print("ok; шаблонов:", len(tpls))
