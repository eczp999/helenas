# -*- coding: utf-8 -*-
"""
Gerador estático do site da Clínica Helenas.

Lê `dados.json` — o arquivo único de conteúdo — e escreve todas as páginas
como HTML estático. Sem Node, sem build de JavaScript, sem dependências:
apenas a biblioteca padrão do Python 3.

    python gerar.py

Nada que esteja em `_pendencias` do dados.json entra na interface. Quando um
dado não está confirmado, o campo — ou a seção inteira — não é renderizado.
"""
import datetime
import hashlib
import html
import io
import json
import os
import re
import struct
import unicodedata
import zlib
from urllib.parse import quote, urlsplit

RAIZ = os.path.dirname(os.path.abspath(__file__))
D = json.load(io.open(os.path.join(RAIZ, "dados.json"), encoding="utf-8"))

C = D["clinica"]
W = D["whatsapp"]
CATS = D["categorias"]
SITE = D["site_url"].rstrip("/")

# Caminho em que o site fica na hospedagem: "/" num domínio próprio,
# "/helenas/" numa página de projeto do GitHub. Só a 404 precisa dele — ela é
# servida em qualquer endereço errado, então os links dela têm de ser
# absolutos, e absoluto sem o prefixo apontaria para fora do site.
BASE = (urlsplit(SITE).path or "").rstrip("/") + "/"


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def apelido(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", sem_acento.lower()).strip("-")


def e(t):
    return html.escape(t or "", quote=True)


def zap(mensagem):
    """Link do WhatsApp com a mensagem codificada uma única vez."""
    return "https://wa.me/%s?text=%s" % (C["whatsapp_numero"], quote(mensagem, safe=""))


def zap_sobre(assunto, modelo="categoria"):
    return zap(W[modelo].replace("{assunto}", assunto))


def maps_url():
    return "https://www.google.com/maps/search/?api=1&query=" + quote(C["maps_busca"])


def maps_embed():
    return "https://www.google.com/maps?q=" + quote(C["maps_busca"]) + "&output=embed"


def escrever(rel, conteudo):
    destino = os.path.join(RAIZ, rel)
    pasta = os.path.dirname(destino)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    io.open(destino, "w", encoding="utf-8", newline="\n").write(conteudo)


def versao():
    """Impressão digital do CSS e do JS, anexada como ?v= nos ativos, para
    que uma atualização não fique escondida atrás do cache do visitante."""
    h = hashlib.sha1()
    for rel in ("assets/css/helenas.css", "assets/js/helenas.js"):
        caminho = os.path.join(RAIZ, rel)
        if os.path.exists(caminho):
            h.update(io.open(caminho, "rb").read())
    return h.hexdigest()[:8]


V = versao()


# ---------------------------------------------------------------------------
# Desenhos
# ---------------------------------------------------------------------------

def selo(classe="marca__selo"):
    """Monograma da casa. Círculo com as iniciais, como no perfil da clínica.
    Substituir pelo vetor original assim que a clínica enviar o arquivo —
    a troca acontece só aqui."""
    return '<span class="%s" aria-hidden="true">ch</span>' % classe


ICO_ZAP = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
           '<path d="M12.04 2c-5.5 0-9.96 4.46-9.96 9.96 0 1.76.46 3.45 1.34 4.96L2 22l5.2-1.36a9.9 9.9 0 0 0 4.84 1.24h.01'
           'c5.5 0 9.96-4.46 9.96-9.96S17.54 2 12.04 2Zm5.8 14.13c-.24.68-1.42 1.32-1.95 1.37-.5.05-.98.23-3.3-.69-2.78-1.1'
           '-4.55-3.95-4.69-4.13-.14-.19-1.12-1.49-1.12-2.84 0-1.35.71-2.02.96-2.29.25-.28.55-.35.73-.35.18 0 .37 0 .53.01'
           '.17.01.4-.06.62.48.24.57.8 1.97.87 2.11.07.14.12.31.02.5-.1.19-.15.31-.29.47-.14.17-.3.37-.43.5-.14.14-.29.29'
           '-.12.57.17.28.74 1.22 1.59 1.98 1.09.97 2.01 1.27 2.29 1.41.28.14.45.12.62-.07.17-.19.71-.83.9-1.11.19-.28.38'
           '-.24.64-.14.26.09 1.65.78 1.94.92.28.14.47.21.54.33.07.11.07.65-.17 1.33Z"/></svg>')

ICO_INSTA = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
             '<path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38'
             '.16.42.36 1.06.41 2.23.06 1.26.07 1.64.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56'
             '-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.26.06-1.64.07-4.85.07s-3.58-.01-4.85-.07'
             'c-1.17-.05-1.8-.25-2.23-.41a3.8 3.8 0 0 1-1.38-.9 3.8 3.8 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23'
             '-.06-1.26-.07-1.64-.07-4.85s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68'
             '1.38-.9.42-.16 1.06-.36 2.23-.41 1.26-.06 1.64-.07 4.85-.07Zm0 1.98c-3.15 0-3.52.01-4.76.07-1.15.05'
             '-1.77.24-2.19.4-.55.21-.94.47-1.35.88-.41.41-.67.8-.88 1.35-.16.42-.35 1.04-.4 2.19-.06 1.24-.07 1.61'
             '-.07 4.76s.01 3.52.07 4.76c.05 1.15.24 1.77.4 2.19.21.55.47.94.88 1.35.41.41.8.67 1.35.88.42.16 1.04.35'
             '2.19.4 1.24.06 1.61.07 4.76.07s3.52-.01 4.76-.07c1.15-.05 1.77-.24 2.19-.4.55-.21.94-.47 1.35-.88.41-.41'
             '.67-.8.88-1.35.16-.42.35-1.04.4-2.19.06-1.24.07-1.61.07-4.76s-.01-3.52-.07-4.76c-.05-1.15-.24-1.77-.4-2.19'
             'a3.6 3.6 0 0 0-.88-1.35 3.6 3.6 0 0 0-1.35-.88c-.42-.16-1.04-.35-2.19-.4-1.24-.06-1.61-.07-4.76-.07Z"/>'
             '<path d="M12 6.9a5.1 5.1 0 1 0 0 10.2 5.1 5.1 0 0 0 0-10.2Zm0 8.41a3.31 3.31 0 1 1 0-6.62 3.31 3.31 0 0 1 0 6.62Z"/>'
             '<circle cx="17.31" cy="6.69" r="1.19"/></svg>')

ICO_MAPA = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            '<path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Z" stroke-linejoin="round"/>'
            '<circle cx="12" cy="10" r="2.6"/></svg>')

ICO_ESTRELA = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
               '<path d="m12 2.6 2.9 5.9 6.5.9-4.7 4.6 1.1 6.5-5.8-3-5.8 3 1.1-6.5L2.6 9.4l6.5-.9L12 2.6Z"/></svg>')

SETA = ('<svg class="seta" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" '
        'aria-hidden="true" focusable="false"><path d="M4 12h15m0 0-5.5-5.5M19 12l-5.5 5.5" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>')

SETA_GRANDE = ('<svg class="indice__seta" viewBox="0 0 32 32" fill="none" stroke="currentColor" '
               'stroke-width="1" aria-hidden="true" focusable="false">'
               '<path d="M7 16h18m0 0-7-7m7 7-7 7" stroke-linecap="round" stroke-linejoin="round"/></svg>')

TRACOS_ICONE = {
    "agenda": '<rect x="3.5" y="5.5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3.5v4m8-4v4" stroke-linecap="round"/>',
    "equipe": '<circle cx="9" cy="8.5" r="3.2"/><path d="M3 19.5c.5-3.2 3-5.2 6-5.2s5.5 2 6 5.2" stroke-linecap="round"/><path d="M16 5.6a3.2 3.2 0 0 1 0 5.8m1.4 3.2c2.1.6 3.5 2.3 3.9 4.9" stroke-linecap="round"/>',
    "folha": '<path d="M20 4C10.5 4 5 8.4 5 14.5c0 2 .6 3.7 1.6 5" stroke-linecap="round"/><path d="M20 4c0 9.5-4.6 14.5-11.5 14.5H6.6" stroke-linecap="round"/><path d="M4 21c1.4-3.6 4-6.4 7.5-8.2" stroke-linecap="round"/>',
    "casa": '<path d="M4 10.2 12 4l8 6.2V19a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 19v-8.8Z" stroke-linejoin="round"/><path d="M9.5 20.5v-6h5v6" stroke-linejoin="round"/>',
    "rosto": '<path d="M12 3.5c4.4 0 7.5 2.8 7.5 7 0 5.2-3.4 10-7.5 10s-7.5-4.8-7.5-10c0-4.2 3.1-7 7.5-7Z" stroke-linejoin="round"/><path d="M9 11h.01M15 11h.01M9.8 15.4c1.4.9 3 .9 4.4 0" stroke-linecap="round"/>',
    "corpo": '<circle cx="12" cy="4.8" r="2.3"/><path d="M12 7.6v7m0 0-3 6m3-6 3 6M6.5 10.5 12 9l5.5 1.5" stroke-linecap="round" stroke-linejoin="round"/>',
    "cabelo": '<path d="M12 3.2c4.3 0 7 3 7 7.2 0 3-.7 5.4-.7 8.2 0 1.2-.8 2-2 2" stroke-linecap="round"/><path d="M12 3.2c-4.3 0-7 3-7 7.2 0 3 .7 5.4.7 8.2 0 1.2.8 2 2 2" stroke-linecap="round"/><path d="M9.4 12.2c1.5 1.1 3.7 1.1 5.2 0" stroke-linecap="round"/>',
    "beleza": '<path d="M12 2.8 13.9 8l5.3 1.9-5.3 1.9L12 17.1 10.1 11.8 4.8 9.9 10.1 8 12 2.8Z" stroke-linejoin="round"/><path d="M18 16.4l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8.8-2.2Z" stroke-linejoin="round"/>',
    "anel": '<circle cx="12" cy="14.5" r="5.5"/><path d="m9.4 9.4 1.3-3.9h2.6l1.3 3.9" stroke-linejoin="round"/>',
    "relogio": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.2V12l3.2 2" stroke-linecap="round"/>',
    "pino": '<path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Z" stroke-linejoin="round"/><circle cx="12" cy="10" r="2.6"/>',
    "fone": '<path d="M6.3 3.8h3.1l1.6 4-2 1.3a12 12 0 0 0 5.9 5.9l1.3-2 4 1.6v3.1a1.8 1.8 0 0 1-2 1.8A16.4 16.4 0 0 1 4.5 5.8a1.8 1.8 0 0 1 1.8-2Z" stroke-linejoin="round"/>',
    "insta": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17" cy="7" r="1" fill="currentColor" stroke="none"/>',
}


def icone(nome, classe=""):
    traco = TRACOS_ICONE.get(nome)
    if not traco:
        return ""
    cls = ' class="%s"' % classe if classe else ""
    return ('<svg%s viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.15" '
            'aria-hidden="true" focusable="false">%s</svg>' % (cls, traco))


def estrelas():
    return '<span class="estrelas" aria-hidden="true">%s</span>' % (ICO_ESTRELA * 5)


# Prefixo relativo da página que está sendo escrita ("", "../", "../../").
# Só `foto()` precisa dele para montar o src, e passá-lo por dez assinaturas
# poluiria o resto do gerador. Cada função de página ajusta antes de montar.
PRE = ""

EXTENSOES_FOTO = (".avif", ".webp", ".jpg", ".jpeg", ".png")


def arquivo_de_foto(id_foto):
    """Procura a foto real em assets/img/fotos/<id>.<ext>. Se existir, o site
    passa a usá-la sozinho no próximo `python gerar.py`."""
    for ext in EXTENSOES_FOTO:
        rel = "assets/img/fotos/%s%s" % (id_foto, ext)
        if os.path.exists(os.path.join(RAIZ, rel)):
            return rel
    return None


def foto(id_foto, alt, classe="foto", rotulo=None, prioritaria=False):
    """Espaço de fotografia. Enquanto a foto real não chega, fica uma
    superfície da marca — nunca banco de imagens, nunca imagem gerada."""
    arquivo = arquivo_de_foto(id_foto)
    if arquivo:
        carga = ('loading="eager" fetchpriority="high"' if prioritaria
                 else 'loading="lazy" fetchpriority="auto"')
        return ('<div class="%s foto--real" data-foto="%s">'
                '<img src="%s%s" alt="%s" %s decoding="async"></div>'
                % (classe, e(id_foto), PRE, e(arquivo), e(alt), carga))
    marca = '<span class="foto__rotulo">%s</span>' % e(rotulo) if rotulo else ""
    return ('<!-- FOTO REAL A INSERIR [%s]: %s -->'
            '<div class="%s" data-foto="%s" role="img" aria-label="%s">%s%s</div>'
            % (e(id_foto), e(alt), classe, e(id_foto), e(alt), selo("marca-selo"), marca))


FOTOS_PEDIDAS = []


def pedir_foto(id_foto, alt, classe="foto", rotulo=None, onde="", prioritaria=False):
    FOTOS_PEDIDAS.append((id_foto, onde, alt, arquivo_de_foto(id_foto)))
    return foto(id_foto, alt, classe, rotulo, prioritaria)


# ---------------------------------------------------------------------------
# Navegação
# ---------------------------------------------------------------------------

NAV = [
    ("a-clinica/", "A Clínica", "01"),
    ("procedimentos/", "Procedimentos", "02"),
    ("noivas/", "Noivas", "03"),
    ("equipe/", "Equipe", "04"),
    ("contato/", "Contato", "05"),
]


def url_abs(rel):
    rel = rel.lstrip("/")
    return SITE + "/" + rel if rel else SITE + "/"


# ---------------------------------------------------------------------------
# Dados estruturados
# ---------------------------------------------------------------------------

def schema_negocio():
    horas = []
    for h in C["horarios"]:
        if not h["abre"]:
            continue
        horas.append({
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": h["schema"],
            "opens": h["abre"],
            "closes": h["fecha"],
        })
    dados = {
        "@type": ["BeautySalon", "HealthAndBeautyBusiness"],
        "@id": SITE + "/#negocio",
        "name": C["nome"],
        "legalName": C["nome_legal"],
        "description": C["assinatura"] + " em " + C["cidade"] + "/" + C["uf"] + ".",
        "url": SITE + "/",
        "telephone": "+" + C["whatsapp_numero"],
        "foundingDate": str(C["fundacao_ano"]),
        "priceRange": "$$",
        "currenciesAccepted": "BRL",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": C["endereco_rua"],
            "addressLocality": C["cidade"],
            "addressRegion": C["uf"],
            "postalCode": C["endereco_cep"],
            "addressCountry": "BR",
        },
        "areaServed": {"@type": "City", "name": C["cidade"]},
        "openingHoursSpecification": horas,
        "sameAs": [C["instagram_url"]],
        "hasMap": maps_url(),
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": C["google_nota"].replace(",", "."),
            "reviewCount": C["google_avaliacoes"],
            "bestRating": "5",
        },
        "makesOffer": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": cat["nome"],
                                               "description": cat["resumo"],
                                               "url": url_abs("procedimentos/%s/" % cat["slug"])}}
            for cat in CATS
        ],
    }
    return dados


def schema_migalhas(trilha):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": nome, "item": url_abs(rel)}
            for i, (rel, nome) in enumerate(trilha)
        ],
    }


def schema_faq(itens):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q["p"],
             "acceptedAnswer": {"@type": "Answer", "text": q["r"]}}
            for q in itens
        ],
    }


def json_ld(blocos):
    grafo = {"@context": "https://schema.org", "@graph": blocos}
    corpo = json.dumps(grafo, ensure_ascii=False, separators=(",", ":"))
    corpo = corpo.replace("</", "<\\/")
    return '<script type="application/ld+json">%s</script>' % corpo


# ---------------------------------------------------------------------------
# Esqueleto da página
# ---------------------------------------------------------------------------

def cabeca(titulo, descricao, rel, pre, blocos_schema, extra=""):
    canonica = url_abs(rel)
    return """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titulo)s</title>
<meta name="description" content="%(descricao)s">
<link rel="canonical" href="%(canonica)s">
<meta name="theme-color" content="#faf6f2">
<meta name="author" content="%(nome)s">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="geo.region" content="BR-%(uf)s">
<meta name="geo.placename" content="%(cidade)s">

<meta property="og:type" content="website">
<meta property="og:site_name" content="%(nome)s">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="%(titulo)s">
<meta property="og:description" content="%(descricao)s">
<meta property="og:url" content="%(canonica)s">
<meta property="og:image" content="%(site)s/assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="%(nome)s — %(assinatura)s em %(cidade)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(titulo)s">
<meta name="twitter:description" content="%(descricao)s">
<meta name="twitter:image" content="%(site)s/assets/img/og.png">

<link rel="icon" href="%(pre)sfavicon.ico" sizes="32x32">
<link rel="icon" href="%(pre)sassets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="%(pre)sassets/img/favicon.svg">

<link rel="preload" href="%(pre)sassets/fonts/cormorant-latin-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="%(pre)sassets/fonts/cormorant-italic-latin-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="%(pre)sassets/fonts/jost-latin-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="%(pre)sassets/css/helenas.css?v=%(v)s">
%(schema)s
%(extra)s
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
""" % {
        "titulo": e(titulo),
        "descricao": e(descricao),
        "canonica": e(canonica),
        "nome": e(C["nome"]),
        "assinatura": e(C["assinatura"]),
        "cidade": e(C["cidade"]),
        "uf": e(C["uf"]),
        "site": e(SITE),
        "pre": pre,
        "v": V,
        "schema": json_ld(blocos_schema),
        "extra": extra,
    }


def marca_html(pre, tag="a"):
    href = ' href="%s"' % (pre if pre else "./") if tag == "a" else ""
    return ('<%(tag)s class="marca"%(href)s>%(selo)s'
            '<span class="marca__texto">'
            '<span class="marca__nome">%(nome)s</span>'
            '<span class="marca__assinatura">%(ass)s</span>'
            '</span></%(tag)s>'
            % {"tag": tag, "href": href, "selo": selo(),
               "nome": e(C["marca"]), "ass": e(C["assinatura"])})


def topo(pre, atual=""):
    links = "".join(
        '<a class="topo__link" href="%s%s"%s>%s</a>'
        % (pre, rel, ' aria-current="page"' if rel == atual else "", e(nome))
        for rel, nome, _ in NAV
    )
    gaveta_links = "".join(
        '<a href="%s%s"%s>%s<span>%s</span></a>'
        % (pre, rel, ' aria-current="page"' if rel == atual else "", e(nome), ordem)
        for rel, nome, ordem in NAV
    )
    return """<header class="topo" data-topo>
<div class="env topo__barra">
%(marca)s
<nav class="topo__nav" aria-label="Navegação principal">%(links)s</nav>
<a class="botao botao--primario topo__acao" href="%(zap)s" target="_blank" rel="noopener">Agendar</a>
<button class="menu-botao" type="button" data-menu-botao aria-expanded="false" aria-controls="gaveta">
<span class="menu-botao__traco" aria-hidden="true"><span></span><span></span><span></span></span>
Menu
</button>
</div>
</header>
<div class="gaveta" id="gaveta" data-gaveta data-aberta="nao">
<nav class="gaveta__lista" aria-label="Navegação">%(gaveta)s</nav>
<div class="gaveta__rodape">
<a class="botao botao--primario" href="%(zap)s" target="_blank" rel="noopener">%(ico)s Agendar pelo WhatsApp</a>
<p class="gaveta__contato"><span>%(tel)s</span><span>%(horario)s</span></p>
</div>
</div>
""" % {
        "marca": marca_html(pre),
        "links": links,
        "gaveta": gaveta_links,
        "zap": e(zap(W["agendar"])),
        "ico": ICO_ZAP,
        "tel": e(C["whatsapp_exibicao"]),
        "horario": e(C["horario_curto"]),
    }


def rodape(pre):
    links_nav = "".join('<li><a href="%s%s">%s</a></li>' % (pre, rel, e(nome))
                        for rel, nome, _ in NAV)
    links_cat = "".join('<li><a href="%sprocedimentos/%s/">%s</a></li>' % (pre, cat["slug"], e(cat["nome"]))
                        for cat in CATS)
    horarios = "".join('<li><span>%s</span> <span>%s</span></li>' % (e(h["dias"]), e(h["texto"]))
                       for h in C["horarios"])
    return """<footer class="rodape">
<div class="env">
<div class="rodape__grade">
<div>
%(marca)s
<p class="rodape__sobre">%(lema)s</p>
</div>
<div>
<p class="rodape__titulo">Navegar</p>
<ul class="rodape__lista">%(nav)s</ul>
</div>
<div>
<p class="rodape__titulo">Procedimentos</p>
<ul class="rodape__lista">%(cats)s</ul>
</div>
<div>
<p class="rodape__titulo">A casa</p>
<ul class="rodape__lista">
<li><a href="%(maps)s" target="_blank" rel="noopener">%(endereco)s</a></li>
<li><a href="tel:+%(numero)s">%(tel)s</a></li>
<li><a href="%(insta)s" target="_blank" rel="noopener">@%(insta_user)s</a></li>
</ul>
<ul class="horarios" style="margin-top:var(--e5)">%(horarios)s</ul>
</div>
</div>
<div class="rodape__fim">
<p>© %(ano)s %(legal)s · CNPJ %(cnpj)s · <a href="%(pre)sprivacidade/">Privacidade</a></p>
<div class="rodape__sociais">
<a href="%(insta)s" target="_blank" rel="noopener" aria-label="Instagram da %(nome)s">%(ico_insta)s</a>
<a href="%(zap)s" target="_blank" rel="noopener" aria-label="WhatsApp da %(nome)s">%(ico_zap)s</a>
<a href="%(maps)s" target="_blank" rel="noopener" aria-label="Como chegar até a %(nome)s">%(ico_mapa_f)s</a>
</div>
</div>
</div>
</footer>
""" % {
        "marca": marca_html(pre, "div"),
        "lema": e(C["lema"]),
        "nav": links_nav,
        "cats": links_cat,
        "maps": e(maps_url()),
        "endereco": e(C["endereco_rua"] + " — " + C["cidade"] + "/" + C["uf"]),
        "numero": e(C["whatsapp_numero"]),
        "tel": e(C["whatsapp_exibicao"]),
        "insta": e(C["instagram_url"]),
        "insta_user": e(C["instagram_usuario"]),
        "horarios": horarios,
        "zap": e(zap(W["conversar"])),
        "ano": datetime.date.today().year,
        "legal": e(C["nome_legal"]),
        "cnpj": e(C["cnpj"]),
        "pre": pre,
        "nome": e(C["nome"]),
        "ico_insta": ICO_INSTA,
        "ico_zap": ICO_ZAP,
        "ico_mapa_f": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Zm0-8.6a2.6 2.6 0 1 1 0-5.2 2.6 2.6 0 0 1 0 5.2Z"/></svg>',
    }


def flutuante():
    return ('<a class="zap" data-zap data-visivel="nao" href="%s" target="_blank" rel="noopener" '
            'aria-label="Falar com a %s pelo WhatsApp">%s</a>'
            % (e(zap(W["conversar"])), e(C["nome"]), ICO_ZAP))


def fim(pre):
    return '%s<script src="%sassets/js/helenas.js?v=%s" defer></script>\n</body>\n</html>\n' % (
        flutuante(), pre, V)


# ---------------------------------------------------------------------------
# Blocos reutilizáveis
# ---------------------------------------------------------------------------

def migalhas(pre, trilha):
    """trilha: lista de (href_relativo_ao_pre|None, nome). O último é o atual."""
    partes = []
    for i, (rel, nome) in enumerate(trilha):
        if i == len(trilha) - 1:
            partes.append('<li aria-current="page">%s</li>' % e(nome))
        else:
            partes.append('<li><a href="%s%s">%s</a></li>' % (pre, rel, e(nome)))
    return ('<nav class="migalhas" aria-label="Você está em"><ol>%s</ol></nav>'
            % "".join(partes))


def intro_pagina(pre, trilha, etiqueta, titulo, texto, acao=None):
    botao = ""
    if acao:
        botao = ('<div style="margin-top:var(--e6)"><a class="botao botao--primario" href="%s" '
                 'target="_blank" rel="noopener">%s %s</a></div>' % (e(acao[1]), ICO_ZAP, e(acao[0])))
    return """<section class="intro-pagina">
<div class="env">
%(migalhas)s
<div class="intro-pagina__grade" style="margin-top:var(--e6)">
<div class="revelar visivel">
<p class="etiqueta">%(etiqueta)s</p>
<h1>%(titulo)s</h1>
</div>
<div class="revelar visivel" data-atraso="1">
<p class="intro-pagina__texto">%(texto)s</p>
%(botao)s
</div>
</div>
</div>
</section>
""" % {"migalhas": migalhas(pre, trilha), "etiqueta": e(etiqueta),
       "titulo": e(titulo), "texto": e(texto), "botao": botao}


def bloco_faq(itens, titulo, etiqueta="Dúvidas", texto=None, fundo=""):
    if not itens:
        return ""
    linhas = "".join(
        '<details class="faq__item"><summary>%s<span class="faq__sinal" aria-hidden="true"></span></summary>'
        '<div class="faq__resposta"><p>%s</p></div></details>' % (e(q["p"]), e(q["r"]))
        for q in itens
    )
    sub = '<p>%s</p>' % e(texto) if texto else ""
    return """<section class="secao %(fundo)s">
<div class="env">
<div class="cabeca-secao revelar">
<p class="etiqueta">%(etiqueta)s</p>
<h2>%(titulo)s</h2>
%(sub)s
</div>
<div class="faq revelar">%(linhas)s</div>
</div>
</section>
""" % {"fundo": fundo, "etiqueta": e(etiqueta), "titulo": e(titulo), "sub": sub, "linhas": linhas}


def bloco_numeros():
    itens = "".join(
        '<div class="numero revelar" data-atraso="%d">'
        '<span class="numero__valor">%s</span>'
        '<span class="numero__rotulo">%s</span>'
        '<span class="numero__detalhe">%s</span></div>'
        % (i % 4, e(n["valor"]), e(n["rotulo"]), e(n["detalhe"]))
        for i, n in enumerate(D["home"]["numeros"])
    )
    return '<section class="secao--curta" aria-label="A clínica em números"><div class="env"><div class="numeros">%s</div></div></section>\n' % itens


def bloco_avaliacoes(fundo="", etiqueta=None, titulo=None):
    h = D["home"]
    cartoes = "".join(
        '<figure class="avaliacao revelar" data-atraso="%d">'
        '%s<blockquote>%s</blockquote>'
        '<figcaption><strong>%s</strong><span>Avaliação no %s</span></figcaption></figure>'
        % (i, estrelas(), e(a["texto"]), e(a["autor"]), e(a["origem"]))
        for i, a in enumerate(D["avaliacoes"])
    )
    return """<section class="secao %(fundo)s">
<div class="env">
<div class="cabeca-secao revelar">
<p class="etiqueta">%(etiqueta)s</p>
<h2>%(titulo)s</h2>
<p class="nota-google">%(estrelas)s <span><strong>%(nota)s</strong> em %(qtd)s avaliações no Google</span></p>
</div>
<div class="avaliacoes">%(cartoes)s</div>
</div>
</section>
""" % {"fundo": fundo,
       "etiqueta": e(etiqueta or h["avaliacoes_etiqueta"]),
       "titulo": e(titulo or h["avaliacoes_titulo"]),
       "estrelas": estrelas(), "nota": e(C["google_nota"]),
       "qtd": C["google_avaliacoes"], "cartoes": cartoes}


def bloco_local(pre, com_form=False):
    horarios = "".join('<li><span>%s</span> <span>%s</span></li>' % (e(h["dias"]), e(h["texto"]))
                       for h in C["horarios"])
    dados = """<div class="dados">
<div class="dado">%(ico_pino)s<div>
<span class="dado__rotulo">Endereço</span>
<a class="dado__valor" href="%(maps)s" target="_blank" rel="noopener">%(rua)s</a>
<p class="dado__extra">%(bairro)s · %(cidade)s/%(uf)s · CEP %(cep)s</p>
</div></div>
<div class="dado">%(ico_fone)s<div>
<span class="dado__rotulo">Telefone e WhatsApp</span>
<a class="dado__valor" href="%(zap)s" target="_blank" rel="noopener">%(tel)s</a>
<p class="dado__extra">O agendamento é feito por aqui.</p>
</div></div>
<div class="dado">%(ico_relogio)s<div>
<span class="dado__rotulo">Horários</span>
<ul class="horarios" style="margin-top:var(--e2)">%(horarios)s</ul>
</div></div>
<div class="dado">%(ico_insta)s<div>
<span class="dado__rotulo">Instagram</span>
<a class="dado__valor" href="%(insta)s" target="_blank" rel="noopener">@%(insta_user)s</a>
<p class="dado__extra">O dia a dia da clínica e os trabalhos da equipe.</p>
</div></div>
</div>""" % {
        "ico_pino": icone("pino"), "ico_fone": icone("fone"),
        "ico_relogio": icone("relogio"), "ico_insta": icone("insta"),
        "maps": e(maps_url()), "rua": e(C["endereco_rua"]),
        "bairro": e(C["bairro"]), "cidade": e(C["cidade"]), "uf": e(C["uf"]),
        "cep": e(C["endereco_cep"]), "zap": e(zap(W["agendar"])),
        "tel": e(C["whatsapp_exibicao"]), "horarios": horarios,
        "insta": e(C["instagram_url"]), "insta_user": e(C["instagram_usuario"]),
    }

    mapa = ('<div class="mapa" data-mapa="%s" data-titulo="Mapa com a localização da %s"></div>'
            % (e(maps_embed()), e(C["nome"])))

    direita = formulario() if com_form else mapa
    extra = ('<div class="env" style="margin-top:var(--e7)">%s</div>' % mapa) if com_form else ""

    return """<section class="secao secao--areia" id="local">
<div class="env">
<div class="cabeca-secao revelar">
<p class="etiqueta">Onde estamos</p>
<h2>Av. Presidente Castelo Branco, 180</h2>
<p>%(horario_frase)s O agendamento é feito pelo WhatsApp e quem responde é a recepção da clínica.</p>
</div>
<div class="local__grade">
<div class="revelar">%(dados)s</div>
<div class="revelar" data-atraso="1">%(direita)s</div>
</div>
</div>
%(extra)s
</section>
""" % {"horario_frase": e(C["horario_frase"]), "dados": dados,
       "direita": direita, "extra": extra}


def formulario():
    return """<form class="formulario" data-form="https://wa.me/%(numero)s" novalidate>
<div class="campo">
<label for="f-nome">Seu nome</label>
<input id="f-nome" name="nome" type="text" required minlength="2" autocomplete="name"
       data-faltando="Diga como podemos te chamar.">
<span class="campo__erro" data-erro role="alert"></span>
</div>
<div class="campo">
<label for="f-tel">Telefone com DDD</label>
<input id="f-tel" name="telefone" type="tel" required minlength="8" autocomplete="tel"
       inputmode="tel" placeholder="(43) 90000-0000"
       data-faltando="Precisamos de um telefone para retornar.">
<span class="campo__erro" data-erro role="alert"></span>
</div>
<div class="campo">
<label for="f-assunto">Sobre o que você quer falar</label>
<select id="f-assunto" name="assunto">
<option value="">Escolha uma opção</option>
%(opcoes)s
<option value="Outro assunto">Outro assunto</option>
</select>
<span class="campo__erro" data-erro role="alert"></span>
</div>
<div class="campo">
<label for="f-msg">Mensagem (opcional)</label>
<textarea id="f-msg" name="mensagem" rows="4"
          placeholder="Conte o que você quer cuidar ou a data que tem em mente."></textarea>
<span class="campo__erro" data-erro role="alert"></span>
</div>
<p class="formulario__aviso" data-aviso hidden></p>
<button class="botao botao--primario" type="submit">%(ico)s Enviar pelo WhatsApp</button>
<p class="formulario__nota">Ao enviar, o formulário abre o WhatsApp com a sua mensagem já escrita.
Nada é armazenado neste site.</p>
</form>""" % {
        "numero": e(C["whatsapp_numero"]),
        "opcoes": "".join('<option value="%s">%s</option>' % (e(cat["nome"]), e(cat["nome"])) for cat in CATS)
                  + '<option value="Dia da Noiva">Dia da Noiva</option>',
        "ico": ICO_ZAP,
    }


def bloco_final(etiqueta=None, titulo=None, texto=None, rotulo=None, mensagem=None, escuro=True):
    h = D["home"]
    classe = "secao final escuro" if escuro else "secao final"
    botao_sec = ('<a class="botao %s" href="%s" target="_blank" rel="noopener">Ver o Instagram</a>'
                 % ("botao--claro" if escuro else "botao--contorno", e(C["instagram_url"])))
    return """<section class="%(classe)s">
<div class="env final__grade">
<p class="etiqueta etiqueta--solta">%(etiqueta)s</p>
<h2>%(titulo)s</h2>
<p class="texto-g">%(texto)s</p>
<div class="final__acoes">
<a class="botao %(bp)s" href="%(zap)s" target="_blank" rel="noopener">%(ico)s %(rotulo)s</a>
%(sec)s
</div>
</div>
</section>
""" % {"classe": classe,
       "etiqueta": e(etiqueta or h["final_etiqueta"]),
       "titulo": e(titulo or h["final_titulo"]),
       "texto": e(texto or h["final_texto"]),
       "bp": "botao--claro" if escuro else "botao--primario",
       "zap": e(zap(mensagem or W["avaliacao"])),
       "ico": ICO_ZAP,
       "rotulo": e(rotulo or h["final_cta"]),
       "sec": botao_sec}


def bloco_noivas_faixa(pre):
    h = D["home"]
    return """<section class="secao escuro faixa-noivas">
<div class="env faixa-noivas__grade">
<div class="revelar">
<p class="etiqueta">%(etiqueta)s</p>
<h2 style="margin-top:var(--e4)">%(titulo)s</h2>
<p class="faixa-noivas__texto">%(texto)s</p>
<div class="faixa-noivas__acao">
<a class="botao botao--claro" href="%(pre)snoivas/">%(rotulo)s %(seta)s</a>
</div>
</div>
<div class="revelar" data-atraso="1">%(foto)s</div>
</div>
</section>
""" % {"etiqueta": e(h["noivas_etiqueta"]), "titulo": e(h["noivas_titulo"]),
       "texto": e(h["noivas_texto"]), "pre": pre, "rotulo": e(h["noivas_cta"]),
       "seta": SETA,
       "foto": pedir_foto("noiva-principal", "Noiva sendo preparada na Clínica Helenas",
                          "foto foto--retrato", "Foto da noiva",
                          onde="Home e página Noivas — imagem principal do Dia da Noiva")}


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

def secao_hero():
    h = D["home"]
    linhas = "".join("<span>%s</span>" % e(l) for l in h["hero_titulo_linhas"])
    return """<section class="hero">
<div class="env hero__grade">
<div class="hero__texto revelar visivel">
<p class="etiqueta">%(etiqueta)s</p>
<h1 class="hero__titulo">%(linhas)s</h1>
<p class="hero__texto">%(texto)s</p>
<div class="hero__acoes">
<a class="botao botao--primario" href="%(zap)s" target="_blank" rel="noopener">%(ico)s %(cta)s</a>
<a class="botao botao--contorno" href="#frentes">%(cta2)s</a>
</div>
<div class="hero__nota">
<span>%(estrelas)s <strong>%(nota)s</strong> em %(qtd)s avaliações no Google</span>
<span>%(horario)s</span>
</div>
</div>
<div class="hero__foto revelar visivel" data-atraso="1">%(foto)s</div>
</div>
</section>
""" % {"etiqueta": e(h["hero_etiqueta"]), "linhas": linhas, "texto": e(h["hero_texto"]),
       "zap": e(zap(W["agendar"])), "ico": ICO_ZAP, "cta": e(h["hero_cta"]),
       "cta2": e(h["hero_cta2"]), "estrelas": estrelas(), "nota": e(C["google_nota"]),
       "qtd": C["google_avaliacoes"], "horario": e(C["horario_curto"]),
       "foto": pedir_foto("hero", "Recepção da Clínica Helenas em Londrina",
                          "foto foto--retrato", "Foto da clínica",
                          onde="Home — imagem do topo, primeira coisa que o visitante vê",
                          prioritaria=True)}


def secao_manifesto():
    h = D["home"]
    paras = "".join("<p>%s</p>" % e(p) for p in h["manifesto_paragrafos"])
    return """<section class="secao">
<div class="env manifesto__grade">
<div class="manifesto__titulo revelar">
<p class="etiqueta">%(etiqueta)s</p>
<h2>%(titulo)s</h2>
</div>
<div class="manifesto__corpo revelar" data-atraso="1">
%(paras)s
<div class="assinatura">
<span class="assinatura__nome">%(nome)s</span>
<span class="assinatura__papel">%(papel)s</span>
</div>
</div>
</div>
</section>
""" % {"etiqueta": e(h["manifesto_etiqueta"]), "titulo": e(h["manifesto_titulo"]),
       "paras": paras, "nome": e(h["manifesto_assinatura"]),
       "papel": e(h["manifesto_assinatura_papel"])}


def secao_indice(pre):
    h = D["home"]
    frentes = [(cat["nome"], cat["resumo"], "procedimentos/%s/" % cat["slug"], cat["slug"]) for cat in CATS]
    frentes.append(("Noivas", D["noivas"]["hero_texto"], "noivas/", "noivas"))

    itens = []
    for i, (nome, resumo, destino, chave) in enumerate(frentes, 1):
        itens.append(
            '<li class="indice__item revelar" data-atraso="%d">'
            '<a class="indice__link" href="%s%s">'
            '<span class="indice__ordem">%02d</span>'
            '<span class="indice__nome">%s</span>'
            '<span class="indice__resumo">%s</span>'
            '%s</a>'
            '%s'
            '</li>'
            % (min(i - 1, 4), pre, destino, i, e(nome), e(resumo), SETA_GRANDE,
               pedir_foto("indice-" + chave, "Atendimento de %s na Clínica Helenas" % nome,
                          "foto indice__mini", None,
                          onde="Home — miniatura que aparece ao passar o mouse na lista “%s”" % nome))
        )
    return """<section class="secao" id="frentes">
<div class="env">
<div class="cabeca-secao revelar">
<p class="etiqueta">%(etiqueta)s</p>
<h2>%(titulo)s</h2>
<p>%(texto)s</p>
</div>
<ul class="indice">%(itens)s</ul>
</div>
</section>
""" % {"etiqueta": e(h["categorias_etiqueta"]), "titulo": e(h["categorias_titulo"]),
       "texto": e(h["categorias_texto"]), "itens": "".join(itens)}


def secao_pilares():
    h = D["home"]
    itens = "".join(
        '<li class="pilar revelar" data-atraso="%d">%s<h3>%s</h3><p>%s</p></li>'
        % (i, icone(p["icone"], "pilar__icone"), e(p["titulo"]), e(p["texto"]))
        for i, p in enumerate(h["pilares"])
    )
    return """<section class="secao secao--areia">
<div class="env">
<div class="cabeca-secao revelar">
<p class="etiqueta">%(etiqueta)s</p>
<h2>%(titulo)s</h2>
</div>
<ul class="pilares">%(itens)s</ul>
</div>
</section>
""" % {"etiqueta": e(h["pilares_etiqueta"]), "titulo": e(h["pilares_titulo"]), "itens": itens}


def secao_espaco():
    h = D["home"]
    return """<section class="secao">
<div class="env">
<div class="cabeca-secao revelar">
<p class="etiqueta">%(etiqueta)s</p>
<h2>%(titulo)s</h2>
<p>%(texto)s</p>
</div>
<div class="espaco__grade">
<div class="espaco__a revelar">%(a)s</div>
<div class="espaco__b revelar" data-atraso="1">%(b)s</div>
<div class="espaco__texto revelar" data-atraso="1">
<p class="etiqueta etiqueta--solta">Londrina</p>
<p class="dado__extra">%(endereco)s</p>
<a class="link-filete" href="%(maps)s" target="_blank" rel="noopener">Como chegar %(seta)s</a>
</div>
<div class="espaco__c revelar" data-atraso="2">%(c)s</div>
<div class="espaco__d revelar" data-atraso="2">%(d)s</div>
</div>
</div>
</section>
""" % {"etiqueta": e(h["espaco_etiqueta"]), "titulo": e(h["espaco_titulo"]),
       "texto": e(h["espaco_texto"]), "endereco": e(C["endereco_completo"]),
       "maps": e(maps_url()), "seta": SETA,
       "a": pedir_foto("espaco-recepcao", "Recepção da Clínica Helenas", "foto foto--paisagem",
                       None, onde="Home — mosaico do espaço, foto maior (recepção)"),
       "b": pedir_foto("espaco-sala", "Sala de atendimento estético", "foto foto--retrato",
                       None, onde="Home — mosaico do espaço, foto vertical (sala de estética)"),
       "c": pedir_foto("espaco-salao", "Área do salão de beleza", "foto foto--quadro",
                       None, onde="Home — mosaico do espaço, foto quadrada (salão)"),
       "d": pedir_foto("espaco-detalhe", "Detalhe da decoração da clínica", "foto foto--larga",
                       None, onde="Home — mosaico do espaço, foto horizontal (detalhe/decoração)")}


def home():
    global PRE
    PRE = ""
    desc = ("Clínica de estética avançada e salão de beleza em Londrina. Pele, cabelo, unhas, "
            "sobrancelhas, maquiagem e Dia da Noiva no mesmo endereço. Agende pelo WhatsApp.")
    schema = [schema_negocio(), schema_faq(D["faq"]),
              {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/",
               "name": C["nome"], "inLanguage": "pt-BR",
               "publisher": {"@id": SITE + "/#negocio"}}]
    partes = [
        cabeca("%s — Estética avançada e salão de beleza em %s" % (C["nome"], C["cidade"]),
               desc, "", "", schema),
        topo("", ""),
        '<main id="conteudo">',
        secao_hero(),
        bloco_numeros(),
        secao_manifesto(),
        secao_indice(""),
        secao_pilares(),
        bloco_noivas_faixa(""),
        secao_espaco(),
        bloco_avaliacoes("secao--veu"),
        bloco_faq(D["faq"][:5], "Antes de marcar", "Dúvidas",
                  "As perguntas que mais chegam pelo WhatsApp."),
        bloco_local(""),
        bloco_final(),
        "</main>",
        rodape(""),
        fim(""),
    ]
    escrever("index.html", "".join(partes))


# ---------------------------------------------------------------------------
# A Clínica
# ---------------------------------------------------------------------------

def pagina_clinica():
    p = D["clinica_pagina"]
    pre = "../"
    global PRE
    PRE = pre
    trilha = [("", "Início"), ("a-clinica/", "A Clínica")]
    historia = "".join("<p>%s</p>" % e(x) for x in p["historia_paragrafos"])
    filosofia = "".join(
        '<li class="pilar revelar" data-atraso="%d"><h3>%s</h3><p>%s</p></li>'
        % (i, e(f["titulo"]), e(f["texto"])) for i, f in enumerate(p["filosofia"])
    )
    schema = [
        schema_negocio(),
        schema_migalhas([("", "Início"), ("a-clinica/", "A Clínica")]),
        {"@type": "AboutPage", "url": url_abs("a-clinica/"), "name": p["hero_titulo"],
         "about": {"@id": SITE + "/#negocio"}},
    ]
    partes = [
        cabeca("A Clínica — %s | %s/%s" % (C["nome"], C["cidade"], C["uf"]),
               "Como a Clínica Helenas funciona: história, forma de trabalho, o espaço e a equipe "
               "de estética avançada e salão de beleza em Londrina.",
               "a-clinica/", pre, schema),
        topo(pre, "a-clinica/"),
        '<main id="conteudo">',
        intro_pagina(pre, trilha, p["hero_etiqueta"], p["hero_titulo"], p["hero_texto"]),
        '<div class="env revelar">%s</div>' % pedir_foto(
            "clinica-fachada", "Fachada da Clínica Helenas na avenida Presidente Castelo Branco",
            "foto foto--banda", "Foto da fachada", onde="A Clínica — imagem de abertura (fachada ou recepção)"),
        """<section class="secao">
<div class="env manifesto__grade">
<div class="manifesto__titulo revelar"><p class="etiqueta">Origem</p><h2>%s</h2></div>
<div class="manifesto__corpo revelar" data-atraso="1">%s</div>
</div>
</section>
""" % (e(p["historia_titulo"]), historia),
        bloco_numeros(),
        """<section class="secao secao--areia">
<div class="env">
<div class="cabeca-secao revelar"><p class="etiqueta">Método</p><h2>%s</h2></div>
<ul class="pilares">%s</ul>
</div>
</section>
""" % (e(p["filosofia_titulo"]), filosofia),
        secao_espaco_clinica(p),
        bloco_noivas_faixa(pre),
        bloco_avaliacoes("secao--veu"),
        bloco_final(),
        "</main>",
        rodape(pre),
        fim(pre),
    ]
    escrever("a-clinica/index.html", "".join(partes))


def secao_espaco_clinica(p):
    return """<section class="secao">
<div class="env">
<div class="cabeca-secao revelar"><p class="etiqueta">O espaço</p><h2>%(titulo)s</h2><p>%(texto)s</p></div>
<div class="espaco__grade">
<div class="espaco__a revelar">%(a)s</div>
<div class="espaco__b revelar" data-atraso="1">%(b)s</div>
<div class="espaco__texto revelar" data-atraso="1">
<p class="etiqueta etiqueta--solta">Visita</p>
<p class="dado__extra">Quem quiser conhecer a estrutura antes de marcar pode combinar uma visita pelo WhatsApp.</p>
<a class="link-filete" href="%(zap)s" target="_blank" rel="noopener">Combinar uma visita %(seta)s</a>
</div>
<div class="espaco__c revelar" data-atraso="2">%(c)s</div>
<div class="espaco__d revelar" data-atraso="2">%(d)s</div>
</div>
</div>
</section>
""" % {"titulo": e(p["espaco_titulo"]), "texto": e(p["espaco_texto"]),
       "zap": e(zap(W["conversar"])), "seta": SETA,
       "a": pedir_foto("clinica-espaco-1", "Sala de estética avançada da Clínica Helenas",
                       "foto foto--paisagem", None, onde="A Clínica — mosaico, sala de estética"),
       "b": pedir_foto("clinica-espaco-2", "Ambiente do salão de beleza", "foto foto--retrato",
                       None, onde="A Clínica — mosaico, salão"),
       "c": pedir_foto("clinica-espaco-3", "Detalhe da recepção", "foto foto--quadro",
                       None, onde="A Clínica — mosaico, recepção"),
       "d": pedir_foto("clinica-espaco-4", "Sala reservada para massagens", "foto foto--larga",
                       None, onde="A Clínica — mosaico, sala de massagem")}


# ---------------------------------------------------------------------------
# Procedimentos — hub e categorias
# ---------------------------------------------------------------------------

def pagina_procedimentos():
    pre = "../"
    global PRE
    PRE = pre
    trilha = [("", "Início"), ("procedimentos/", "Procedimentos")]
    cartoes = "".join(
        '<article class="cat revelar" data-atraso="%d">'
        '<a class="cat__midia" href="%s%s/">%s</a>'
        '<div class="cat__texto">'
        '<p class="etiqueta">%s</p>'
        '<h2><a href="%s%s/">%s</a></h2>'
        '<p>%s</p>'
        '<a class="link-filete" href="%s%s/">Ver os procedimentos %s</a>'
        '</div></article>'
        % (i % 2, "", cat["slug"],
           pedir_foto("cat-" + cat["slug"], "Procedimentos de %s" % cat["nome"], "foto",
                      None, onde="Procedimentos — cartão da categoria %s" % cat["nome"]),
           e(cat["etiqueta"]), "", cat["slug"], e(cat["nome"]), e(cat["resumo"]),
           "", cat["slug"], SETA)
        for i, cat in enumerate(CATS)
    )
    schema = [
        schema_negocio(),
        schema_migalhas([("", "Início"), ("procedimentos/", "Procedimentos")]),
        {"@type": "CollectionPage", "url": url_abs("procedimentos/"), "name": "Procedimentos",
         "mainEntity": {"@type": "ItemList", "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "name": cat["nome"],
              "url": url_abs("procedimentos/%s/" % cat["slug"])}
             for i, cat in enumerate(CATS)]}},
    ]
    partes = [
        cabeca("Procedimentos — %s | Estética e beleza em %s" % (C["nome"], C["cidade"]),
               "Estética facial, corpo e bem-estar, cabelo e Head Spa, sobrancelhas, unhas e "
               "maquiagem. Conheça os procedimentos da Clínica Helenas, em Londrina.",
               "procedimentos/", pre, schema),
        topo(pre, "procedimentos/"),
        '<main id="conteudo">',
        intro_pagina(pre, trilha, "Procedimentos", "Quatro frentes de cuidado, uma casa",
                     "A clínica atende pele, corpo, cabelo e beleza no mesmo endereço — e as noivas "
                     "têm um caminho próprio. Escolha por onde começar.",
                     ("Falar com a recepção", zap(W["conversar"]))),
        '<section class="secao secao--curta"><div class="env"><div class="cats">%s</div></div></section>' % cartoes,
        bloco_noivas_faixa(pre),
        bloco_faq(D["faq"], "Perguntas frequentes", "Dúvidas", None, "secao--areia"),
        bloco_final(),
        "</main>",
        rodape(pre),
        fim(pre),
    ]
    escrever("procedimentos/index.html", "".join(partes))


def pagina_categoria(cat):
    pre = "../../"
    global PRE
    PRE = pre
    rel = "procedimentos/%s/" % cat["slug"]
    trilha = [("", "Início"), ("procedimentos/", "Procedimentos"), (rel, cat["nome"])]

    linhas = []
    for i, proc in enumerate(cat["procedimentos"], 1):
        duracao = ""
        if proc.get("duracao"):
            duracao = ('<p class="proc__duracao">%s Duração aproximada: %s</p>'
                       % (icone("relogio"), e(proc["duracao"])))
        linhas.append(
            '<li class="proc__item revelar"><div class="proc__linha">'
            '<span class="proc__ordem">%02d</span>'
            '<div class="proc__cabeca"><h3>%s</h3><p class="proc__resumo">%s</p>%s</div>'
            '<div class="proc__corpo">'
            '<p>%s</p>'
            '<dl class="proc__indicacao"><dt>Para quem</dt><dd>%s</dd></dl>'
            '<a class="link-filete proc__acao" href="%s" target="_blank" rel="noopener">'
            'Perguntar sobre %s %s</a>'
            '</div></div></li>'
            % (i, e(proc["nome"]), e(proc["resumo"]), duracao, e(proc["detalhe"]),
               e(proc["indicacao"]),
               e(zap_sobre(proc["nome"], "procedimento")), e(proc["nome"].lower()), SETA)
        )

    outras = "".join(
        '<li class="indice__item"><a class="indice__link" href="%s%s/">'
        '<span class="indice__ordem">%02d</span>'
        '<span class="indice__nome">%s</span>'
        '<span class="indice__resumo">%s</span>%s</a></li>'
        % ("../", o["slug"], i + 1, e(o["nome"]), e(o["resumo"]), SETA_GRANDE)
        for i, o in enumerate(CATS) if o["slug"] != cat["slug"]
    )

    schema = [
        schema_negocio(),
        schema_migalhas([("", "Início"), ("procedimentos/", "Procedimentos"), (rel, cat["nome"])]),
        {"@type": "Service", "name": cat["nome"], "description": cat["resumo"],
         "url": url_abs(rel), "provider": {"@id": SITE + "/#negocio"},
         "areaServed": {"@type": "City", "name": C["cidade"]},
         "hasOfferCatalog": {"@type": "OfferCatalog", "name": cat["nome"], "itemListElement": [
             {"@type": "Offer", "itemOffered": {"@type": "Service", "name": p["nome"],
                                                "description": p["resumo"]}}
             for p in cat["procedimentos"]]}},
    ]
    if cat.get("faq"):
        schema.append(schema_faq(cat["faq"]))

    partes = [
        cabeca("%s — %s | %s/%s" % (cat["nome"], C["nome"], C["cidade"], C["uf"]),
               cat["resumo"], rel, pre, schema),
        topo(pre, "procedimentos/"),
        '<main id="conteudo">',
        intro_pagina(pre, trilha, cat["etiqueta"], cat["chamada"], cat["descricao"],
                     ("Agendar avaliação", zap_sobre(cat["nome"]))),
        '<div class="env revelar">%s</div>' % pedir_foto(
            "cat-topo-" + cat["slug"], "Atendimento de %s na Clínica Helenas" % cat["nome"].lower(),
            "foto foto--banda", None, onde="Categoria %s — imagem de abertura" % cat["nome"]),
        '<section class="secao"><div class="env">'
        '<div class="cabeca-secao revelar"><p class="etiqueta">O que fazemos</p>'
        '<h2>%s</h2></div>'
        '<ul class="proc">%s</ul></div></section>' % (e(cat["nome"]), "".join(linhas)),
        bloco_faq(cat.get("faq", []), "Sobre %s" % cat["nome"].lower(), "Dúvidas", None, "secao--areia"),
        '<section class="secao"><div class="env">'
        '<div class="cabeca-secao revelar"><p class="etiqueta">Continue</p>'
        '<h2>Outras frentes da casa</h2></div>'
        '<ul class="indice">%s</ul></div></section>' % outras,
        bloco_final(
            "Avaliação",
            "Vamos ver isso de perto",
            "A avaliação presencial é o que define o protocolo. Conte pelo WhatsApp o que você quer "
            "cuidar e a recepção encaixa um horário.",
            "Agendar avaliação",
            zap_sobre(cat["nome"])),
        "</main>",
        rodape(pre),
        fim(pre),
    ]
    escrever(rel + "index.html", "".join(partes))


# ---------------------------------------------------------------------------
# Noivas
# ---------------------------------------------------------------------------

def pagina_noivas():
    n = D["noivas"]
    pre = "../"
    global PRE
    PRE = pre
    trilha = [("", "Início"), ("noivas/", "Noivas")]

    intro = "".join("<p>%s</p>" % e(x) for x in n["intro_paragrafos"])
    etapas = "".join(
        '<li class="etapa revelar"><div class="etapa__marco">'
        '<span class="etapa__quando">%s</span><h3>%s</h3></div>'
        '<p>%s</p></li>'
        % (e(x["quando"]), e(x["marco"]), e(x["texto"]))
        for x in n["cronograma"]
    )
    inclui = "".join("<li>%s</li>" % e(x) for x in n["inclui"])
    faq_noivas = [q for q in D["faq"] if "casamento" in q["p"].lower() or "noiva" in q["p"].lower()]

    schema = [
        schema_negocio(),
        schema_migalhas([("", "Início"), ("noivas/", "Noivas")]),
        {"@type": "Service", "name": "Dia da Noiva", "url": url_abs("noivas/"),
         "description": n["hero_texto"], "provider": {"@id": SITE + "/#negocio"},
         "areaServed": {"@type": "City", "name": C["cidade"]},
         "serviceType": "Dia da Noiva"},
    ]
    if faq_noivas:
        schema.append(schema_faq(faq_noivas))

    partes = [
        cabeca("Dia da Noiva em %s — %s" % (C["cidade"], C["nome"]),
               "Consultoria de beleza de noiva com Julia Helenas: cronograma de pele, prova de "
               "maquiagem e penteado e o Dia da Noiva completo, em Londrina.",
               "noivas/", pre, schema),
        topo(pre, "noivas/"),
        '<main id="conteudo">',
        intro_pagina(pre, trilha, n["etiqueta"], n["hero_titulo"], n["hero_texto"],
                     ("Falar sobre o meu casamento", zap(W["noiva"]))),
        """<section class="secao secao--curta">
<div class="env manifesto__grade">
<div class="manifesto__titulo revelar"><p class="etiqueta">Especialidade</p><h2>%(titulo)s</h2></div>
<div class="manifesto__corpo revelar" data-atraso="1">%(intro)s</div>
</div>
</section>
<div class="env revelar">%(foto)s</div>
""" % {"titulo": e(n["intro_titulo"]), "intro": intro,
       "foto": pedir_foto("noivas-abertura", "Noiva pronta após o Dia da Noiva na Clínica Helenas",
                          "foto foto--banda", "Foto de noiva",
                          onde="Noivas — imagem de abertura (noiva pronta)")},
        """<section class="secao">
<div class="env">
<div class="cabeca-secao revelar"><p class="etiqueta">Cronograma</p><h2>%(titulo)s</h2><p>%(nota)s</p></div>
<ol class="cronograma">%(etapas)s</ol>
</div>
</section>
""" % {"titulo": e(n["cronograma_titulo"]), "nota": e(n["cronograma_nota"]), "etapas": etapas},
        """<section class="secao escuro">
<div class="env">
<div class="cabeca-secao revelar"><p class="etiqueta">O pacote</p><h2>%(titulo)s</h2><p>%(nota)s</p></div>
<ul class="inclui revelar">%(inclui)s</ul>
<div style="margin-top:var(--e8);display:grid;gap:var(--e4);max-width:58ch">
<h3 style="font-size:var(--t-h3)">%(acomp_titulo)s</h3>
<p>%(acomp_texto)s</p>
</div>
</div>
</section>
""" % {"titulo": e(n["inclui_titulo"]), "nota": e(n["inclui_nota"]), "inclui": inclui,
       "acomp_titulo": e(n["acompanhantes_titulo"]), "acomp_texto": e(n["acompanhantes_texto"])},
        bloco_faq(faq_noivas, "Sobre o casamento", "Dúvidas", None, "secao--areia"),
        bloco_avaliacoes("", "Vocês", "Quem passou por aqui"),
        bloco_final(n["etiqueta"], n["cta_titulo"], n["cta_texto"], n["cta_rotulo"], W["noiva"]),
        "</main>",
        rodape(pre),
        fim(pre),
    ]
    escrever("noivas/index.html", "".join(partes))


# ---------------------------------------------------------------------------
# Equipe
# ---------------------------------------------------------------------------

def pagina_equipe():
    q = D["equipe_pagina"]
    pre = "../"
    global PRE
    PRE = pre
    trilha = [("", "Início"), ("equipe/", "Equipe")]

    destaques = [m for m in D["equipe"] if m.get("destaque")]
    demais = [m for m in D["equipe"] if not m.get("destaque")]

    blocos = []
    for m in destaques:
        bio = "".join("<p>%s</p>" % e(x) for x in m.get("bio", []))
        areas = "".join('<span class="marca-area">%s</span>' % e(a) for a in m.get("areas", []))
        insta = ""
        if m.get("instagram_url"):
            insta = ('<a class="link-filete" href="%s" target="_blank" rel="noopener" '
                     'style="margin-top:var(--e3)">@%s %s</a>'
                     % (e(m["instagram_url"]), e(m["instagram_usuario"]), SETA))
        blocos.append(
            '<section class="secao secao--curta"><div class="env perfil">'
            '<div class="revelar">%s</div>'
            '<div class="perfil__texto revelar" data-atraso="1">'
            '<span class="perfil__papel">%s</span><h2>%s</h2>'
            '<div class="perfil__bio">%s</div>'
            '<div class="perfil__areas">%s</div>%s'
            '</div></div></section>'
            % (pedir_foto("equipe-" + apelido(m["nome"]), "Retrato de %s" % m["nome"],
                          "foto foto--retrato", None,
                          onde="Equipe — retrato de %s" % m["nome"]),
               e(m["papel"]), e(m["nome"]), bio, areas, insta)
        )

    grade = ""
    if demais:
        cartoes = "".join(
            '<article class="membro revelar" data-atraso="%d">%s'
            '<div><span class="perfil__papel">%s</span><h3 style="margin-top:var(--e2)">%s</h3></div>'
            '<div class="perfil__areas">%s</div></article>'
            % (i, pedir_foto("equipe-" + apelido(m["nome"]), "Retrato de %s" % m["nome"],
                             "foto", None, onde="Equipe — retrato de %s" % m["nome"]),
               e(m["papel"]), e(m["nome"]),
               "".join('<span class="marca-area">%s</span>' % e(a) for a in m.get("areas", [])))
            for i, m in enumerate(demais)
        )
        grade = ('<section class="secao secao--areia"><div class="env">'
                 '<div class="cabeca-secao revelar"><p class="etiqueta">Também cuidam de você</p>'
                 '<h2>A equipe da casa</h2></div>'
                 '<div class="equipe-grade">%s</div></div></section>' % cartoes)

    pessoas = [
        {"@type": "Person", "name": m["nome"], "jobTitle": m["papel"],
         "worksFor": {"@id": SITE + "/#negocio"},
         **({"sameAs": [m["instagram_url"]]} if m.get("instagram_url") else {})}
        for m in D["equipe"]
    ]
    schema = [schema_negocio(), schema_migalhas([("", "Início"), ("equipe/", "Equipe")])] + pessoas

    partes = [
        cabeca("Equipe — %s | %s/%s" % (C["nome"], C["cidade"], C["uf"]),
               "Conheça quem atende na Clínica Helenas: Julia Helenas, biomédica esteta e "
               "fundadora, e a equipe de maquiagem, cabelo e terapias em Londrina.",
               "equipe/", pre, schema),
        topo(pre, "equipe/"),
        '<main id="conteudo">',
        intro_pagina(pre, trilha, q["etiqueta"], q["titulo"], q["texto"]),
        "".join(blocos),
        grade,
        bloco_avaliacoes("secao--veu"),
        bloco_final(),
        "</main>",
        rodape(pre),
        fim(pre),
    ]
    escrever("equipe/index.html", "".join(partes))


# ---------------------------------------------------------------------------
# Contato
# ---------------------------------------------------------------------------

def pagina_contato():
    c = D["contato_pagina"]
    pre = "../"
    global PRE
    PRE = pre
    trilha = [("", "Início"), ("contato/", "Contato")]
    schema = [
        schema_negocio(),
        schema_migalhas([("", "Início"), ("contato/", "Contato")]),
        {"@type": "ContactPage", "url": url_abs("contato/"), "name": "Contato"},
    ]
    partes = [
        cabeca("Contato e localização — %s | %s/%s" % (C["nome"], C["cidade"], C["uf"]),
               "Av. Presidente Castelo Branco, 180, Londrina/PR. Agende pelo WhatsApp "
               "(43) 99199-4020. Terça a sábado, das 9h às 18h30.",
               "contato/", pre, schema),
        topo(pre, "contato/"),
        '<main id="conteudo">',
        intro_pagina(pre, trilha, c["etiqueta"], c["titulo"], c["texto"],
                     ("Abrir o WhatsApp", zap(W["agendar"]))),
        bloco_local(pre, com_form=True),
        bloco_faq(D["faq"], "Perguntas frequentes", "Dúvidas"),
        bloco_final(),
        "</main>",
        rodape(pre),
        fim(pre),
    ]
    escrever("contato/index.html", "".join(partes))


# ---------------------------------------------------------------------------
# Páginas auxiliares
# ---------------------------------------------------------------------------

def pagina_privacidade():
    pre = "../"
    global PRE
    PRE = pre
    corpo = """<div class="prosa revelar">
<p class="texto-g">Este site é institucional e estático. Ele não tem cadastro, não tem área
de cliente e não guarda nada do que você escreve.</p>

<h2>O formulário de contato</h2>
<p>O formulário da página de contato não envia dados para nenhum servidor. Ele monta uma
mensagem com o que você escreveu e abre o WhatsApp da clínica com esse texto já pronto. A
conversa a partir daí acontece dentro do WhatsApp, sob a política de privacidade do próprio
aplicativo.</p>

<h2>Cookies</h2>
<p>O site não usa cookies de rastreamento, não tem pixel de rede social e não roda ferramenta
de análise de audiência.</p>

<h2>Conteúdo de terceiros</h2>
<p>Duas coisas na página vêm de fora e podem registrar o seu acesso conforme as políticas de
quem as fornece:</p>
<ul>
<li>o mapa do Google Maps, carregado só quando você rola até a seção de localização;</li>
<li>os links para WhatsApp e Instagram, que levam você para fora deste site.</li>
</ul>
<p>As fontes tipográficas são servidas pelo próprio site, sem chamada a servidores externos.</p>

<h2>Dados que a clínica guarda</h2>
<p>Quando você agenda um atendimento, a Clínica Helenas registra os dados necessários para
prestar o serviço — nome, contato e informações relevantes de anamnese. Esse tratamento
acontece fora deste site e segue a Lei Geral de Proteção de Dados (Lei 13.709/2018). Para
pedir acesso, correção ou exclusão dos seus dados, fale com a clínica pelo WhatsApp
%(tel)s.</p>

<h2>Responsável</h2>
<p>%(legal)s — CNPJ %(cnpj)s. %(endereco)s</p>
</div>""" % {"tel": e(C["whatsapp_exibicao"]), "legal": e(C["nome_legal"]),
             "cnpj": e(C["cnpj"]), "endereco": e(C["endereco_completo"])}

    schema = [schema_negocio(), schema_migalhas([("", "Início"), ("privacidade/", "Privacidade")])]
    partes = [
        cabeca("Privacidade — %s" % C["nome"],
               "Como este site trata os seus dados: sem cookies de rastreamento, sem armazenamento "
               "de formulário e com mapa carregado sob demanda.",
               "privacidade/", pre, schema),
        topo(pre),
        '<main id="conteudo">',
        intro_pagina(pre, [("", "Início"), ("privacidade/", "Privacidade")], "Jurídico",
                     "Privacidade", "O que este site faz — e o que ele não faz — com as suas informações."),
        '<section class="secao secao--curta"><div class="env">%s</div></section>' % corpo,
        "</main>",
        rodape(pre),
        fim(pre),
    ]
    escrever("privacidade/index.html", "".join(partes))


def pagina_404():
    # A 404 responde por endereços de qualquer profundidade, então tudo nela
    # — inclusive os ativos do cabeçalho e do rodapé — sai do caminho base.
    global PRE
    PRE = BASE
    atalhos = "".join(
        '<li class="indice__item"><a class="indice__link" href="%s%s">'
        '<span class="indice__ordem">%s</span><span class="indice__nome">%s</span>%s</a></li>'
        % (BASE, rel, ordem, e(nome), SETA_GRANDE)
        for rel, nome, ordem in NAV
    )
    schema = [schema_negocio()]
    partes = [
        cabeca("Página não encontrada — %s" % C["nome"],
               "Esta página não existe mais ou o endereço foi digitado com alguma diferença.",
               "404.html", "", schema,
               extra='<meta name="robots" content="noindex, follow">'),
        topo(BASE),
        '<main id="conteudo">',
        """<section class="erro"><div class="env erro__grade">
<span class="erro__codigo" aria-hidden="true">404</span>
<p class="etiqueta etiqueta--solta">Endereço não encontrado</p>
<h1 style="font-size:var(--t-h2)">Esta página não existe</h1>
<p class="texto-g">Pode ser um link antigo ou um endereço digitado com alguma diferença.
Abaixo estão os caminhos da casa.</p>
<div class="final__acoes">
<a class="botao botao--primario" href="%s">Voltar ao início</a>
<a class="botao botao--contorno" href="%s" target="_blank" rel="noopener">Falar pelo WhatsApp</a>
</div>
</div></section>
<section class="secao secao--curta"><div class="env"><ul class="indice">%s</ul></div></section>
""" % (BASE, e(zap(W["conversar"])), atalhos),
        "</main>",
        rodape(BASE),
        fim(BASE),
    ]
    escrever("404.html", "".join(partes))


# ---------------------------------------------------------------------------
# Ativos gerados
# ---------------------------------------------------------------------------

def paginas_publicadas():
    itens = [("", "1.0"), ("a-clinica/", "0.8"), ("procedimentos/", "0.9")]
    itens += [("procedimentos/%s/" % cat["slug"], "0.8") for cat in CATS]
    itens += [("noivas/", "0.9"), ("equipe/", "0.7"), ("contato/", "0.8"), ("privacidade/", "0.3")]
    return itens


def sitemap():
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for rel, prio in paginas_publicadas():
        linhas.append("<url><loc>%s</loc><changefreq>monthly</changefreq><priority>%s</priority></url>"
                      % (url_abs(rel), prio))
    linhas.append("</urlset>")
    escrever("sitemap.xml", "\n".join(linhas) + "\n")


def robots():
    escrever("robots.txt",
             "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)


def favicon_svg():
    escrever("assets/img/favicon.svg",
             '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
             '<rect width="64" height="64" rx="12" fill="#faf6f2"/>'
             '<circle cx="32" cy="32" r="25" fill="none" stroke="#b8807c" stroke-width="2.5"/>'
             '<text x="32" y="43" text-anchor="middle" font-family="Georgia,\'Times New Roman\',serif" '
             'font-size="30" fill="#8f5a56" letter-spacing="-1">ch</text></svg>\n')


def _png(largura, altura, pixels):
    """PNG mínimo, sem dependências. `pixels` é bytes RGB por linha."""
    def bloco(tipo, dados):
        c = tipo + dados
        return struct.pack(">I", len(dados)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    cru = b"".join(b"\x00" + pixels[y] for y in range(altura))
    return (b"\x89PNG\r\n\x1a\n"
            + bloco(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0))
            + bloco(b"IDAT", zlib.compress(cru, 9))
            + bloco(b"IEND", b""))


def _cor(h):
    return bytes(int(h[i:i + 2], 16) for i in (0, 2, 4))


def favicon_ico():
    """Ícone 32×32: círculo rosé sobre marfim, no espírito do monograma."""
    n = 32
    fundo, traco = _cor("faf6f2"), _cor("8f5a56")
    linhas = []
    for y in range(n):
        linha = bytearray()
        for x in range(n):
            dx, dy = x - 15.5, y - 15.5
            d = (dx * dx + dy * dy) ** 0.5
            linha += traco if 11.0 <= d <= 13.2 else fundo
        linhas.append(bytes(linha))
    png = _png(n, n, linhas)
    cabecalho = struct.pack("<HHH", 0, 1, 1)
    entrada = struct.pack("<BBBBHHII", n, n, 0, 0, 1, 32, len(png), 22)
    io.open(os.path.join(RAIZ, "favicon.ico"), "wb").write(cabecalho + entrada + png)


def og_imagem():
    """Cartão de compartilhamento 1200×630: campo de marfim com moldura dourada
    e a marca d'água circular. Substituir por um cartão com fotografia real —
    ver `_pendencias.fotografia` no dados.json."""
    L, A = 1200, 630
    marfim, ouro, rose = _cor("faf6f2"), _cor("b08d57"), _cor("e0c6bf")
    cx, cy = L / 2.0, A / 2.0
    linhas = []
    for y in range(A):
        linha = bytearray()
        for x in range(L):
            # véu rosé no canto superior direito
            dv = (((x - L * 0.86) ** 2) + ((y + A * 0.15) ** 2)) ** 0.5
            base = rose if dv < 420 else marfim
            # moldura dupla
            na_moldura = (
                (44 <= x <= L - 45 and 44 <= y <= A - 45)
                and not (46 <= x <= L - 47 and 46 <= y <= A - 47)
            ) or (
                (56 <= x <= L - 57 and 56 <= y <= A - 57)
                and not (57 <= x <= L - 58 and 57 <= y <= A - 58)
            )
            # anel do monograma
            d = (((x - cx) ** 2) + ((y - cy) ** 2)) ** 0.5
            no_anel = 128.0 <= d <= 131.0
            linha += ouro if (na_moldura or no_anel) else base
        linhas.append(bytes(linha))
    io.open(os.path.join(RAIZ, "assets/img/og.png"), "wb").write(_png(L, A, linhas))


# ---------------------------------------------------------------------------
# Principal
# ---------------------------------------------------------------------------

def principal():
    home()
    pagina_clinica()
    pagina_procedimentos()
    for cat in CATS:
        pagina_categoria(cat)
    pagina_noivas()
    pagina_equipe()
    pagina_contato()
    pagina_privacidade()
    pagina_404()
    sitemap()
    robots()
    favicon_svg()
    favicon_ico()
    og_imagem()

    vistos = {}
    for id_foto, onde, alt, arquivo in FOTOS_PEDIDAS:
        vistos.setdefault(id_foto, (onde, alt, arquivo))
    faltam = [i for i, (o, a, arq) in vistos.items() if not arq]
    escrever("_fonte/fotos-pendentes.txt",
             "Espaços de fotografia do site.\n\n"
             "Para preencher: salve a imagem em assets/img/fotos/<id>.jpg (ou .webp,\n"
             ".avif, .png) e rode `python gerar.py`. O site passa a usar a foto real\n"
             "sozinho — não é preciso editar HTML.\n\n"
             "%d de %d preenchidas.\n\n" % (len(vistos) - len(faltam), len(vistos))
             + "\n".join("[%s] %-26s %s\n%33s alt: %s\n"
                         % ("ok" if arq else "  ", i, o, "", a)
                         for i, (o, a, arq) in sorted(vistos.items())))

    print("Site gerado. Versão dos ativos: %s" % V)
    print("%d páginas. Fotos reais: %d de %d."
          % (len(paginas_publicadas()) + 1, len(vistos) - len(faltam), len(vistos)))
    if D.get("_site_url_pendente"):
        print("Atenção: `site_url` ainda é provisório (%s). Trocar antes de publicar." % SITE)


if __name__ == "__main__":
    principal()
