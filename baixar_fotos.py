"""Baixa a foto principal de cada item "só site" para a pasta fotos/.
Uso: coloque este arquivo na mesma pasta do index.html e execute (precisa de internet e Python 3).
Pode rodar de novo: pula o que já foi baixado."""
import json, os, re, sys, time, urllib.request, urllib.parse

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(AQUI, 'fotos')
os.makedirs(PASTA, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0'}

def pega(url, binario=False):
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                d = r.read()
                return d if binario else d.decode('utf-8', 'ignore')
        except Exception:
            time.sleep(1.5)
    return None

itens = json.load(open(os.path.join(AQUI, 'lista_fotos.json'), encoding='utf-8'))
ok = falha = 0
for i, (codigo, link) in enumerate(itens, 1):
    nome = re.sub(r'[^A-Za-z0-9]', '', codigo).upper() + '.jpg'
    destino = os.path.join(PASTA, nome)
    if os.path.exists(destino):
        ok += 1
        continue
    html = pega(link) if link else None
    # nomes de foto podem ter espaco (ex.: "DDF487 001050409.jpg")
    achadas = re.findall(r'https?://storagesitemakita\.blob\.core\.windows\.net/arquivos/[^"\'<>\r\n]+?\.(?:jpg|jpeg|png)', html or '', re.I)
    fotos = [f for f in dict.fromkeys(achadas) if 'logo' not in f.lower()]
    m = re.match(r'[A-Z]*\d+', codigo.upper())
    radical = m.group(0) if m else codigo.upper()
    foto = next((f for f in fotos if codigo.upper() in f.upper()), None) or next((f for f in fotos if radical in f.upper()), None) or (fotos[0] if fotos else None)
    if foto:
        foto = urllib.parse.quote(foto, safe=':/%')
    dados = pega(foto, True) if foto else None
    if dados and len(dados) > 2000:
        open(destino, 'wb').write(dados)
        ok += 1
    else:
        falha += 1
        print('sem foto:', codigo, link)
    print(f'{i}/{len(itens)}', end='\r')
print(f'\nBaixadas: {ok}  Sem foto: {falha}')
