# -*- coding: utf-8 -*-
"""
Gerador do site da Clínica Helenas — V2, página única.

Lê `dados.json` e escreve um único `index.html`, mais sitemap, robots,
favicons e o cartão de compartilhamento. Sem Node, sem framework, sem build
de JavaScript: só a biblioteca padrão do Python 3.

    python gerar.py

Nada que esteja em `_pendencias` entra na interface. O conteúdo aprofundado
mora em modais que já vêm no HTML — nunca buscados por fetch, para que
procedimentos e Dia da Noiva continuem indexáveis.
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
BASE = (urlsplit(SITE).path or "").rstrip("/") + "/"


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def apelido(texto):
    sem = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", sem.lower()).strip("-")


def e(t):
    return html.escape(t or "", quote=True)


def zap(mensagem):
    return "https://wa.me/%s?text=%s" % (C["whatsapp_numero"], quote(mensagem, safe=""))


def zap_sobre(assunto, modelo="categoria"):
    return zap(W[modelo].replace("{assunto}", assunto))


def maps_url():
    return "https://www.google.com/maps/search/?api=1&query=" + quote(C["maps_busca"])


def maps_embed():
    return "https://www.google.com/maps?q=" + quote(C["maps_busca"]) + "&output=embed"


def absolutizar(bloco, ancoras=True):
    """A 404 do GitHub Pages responde por endereços de QUALQUER profundidade
    (/helenas/qualquer/coisa), e um caminho relativo ali resolveria contra uma
    pasta que não existe. Tudo o que ela carrega e aponta sai do caminho base.
    Com `ancoras=False` as âncoras ficam locais - é o caso do link "pular para
    o conteúdo", que aponta para um alvo da própria 404."""
    bloco = bloco.replace('href="assets/', 'href="%sassets/' % BASE)
    bloco = bloco.replace('src="assets/', 'src="%sassets/' % BASE)
    bloco = bloco.replace('href="favicon.ico"', 'href="%sfavicon.ico"' % BASE)
    if ancoras:
        bloco = bloco.replace('href="#', 'href="%s#' % BASE)
    return bloco


def escrever(rel, conteudo):
    destino = os.path.join(RAIZ, rel)
    pasta = os.path.dirname(destino)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    io.open(destino, "w", encoding="utf-8", newline="\n").write(conteudo)


def versao():
    h = hashlib.sha1()
    for rel in ("assets/css/helenas.css", "assets/js/app.js"):
        caminho = os.path.join(RAIZ, rel)
        if os.path.exists(caminho):
            h.update(io.open(caminho, "rb").read())
    return h.hexdigest()[:8]


V = versao()


# ---------------------------------------------------------------------------
# Desenhos
# ---------------------------------------------------------------------------

ICO_ZAP = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
           '<path d="M12.04 2c-5.5 0-9.96 4.46-9.96 9.96 0 1.76.46 3.45 1.34 4.96L2 22l5.2-1.36a9.9 9.9 0 0 0 4.84 1.24h.01'
           'c5.5 0 9.96-4.46 9.96-9.96S17.54 2 12.04 2Zm5.8 14.13c-.24.68-1.42 1.32-1.95 1.37-.5.05-.98.23-3.3-.69-2.78-1.1'
           '-4.55-3.95-4.69-4.13-.14-.19-1.12-1.49-1.12-2.84 0-1.35.71-2.02.96-2.29.25-.28.55-.35.73-.35.18 0 .37 0 .53.01'
           '.17.01.4-.06.62.48.24.57.8 1.97.87 2.11.07.14.12.31.02.5-.1.19-.15.31-.29.47-.14.17-.3.37-.43.5-.14.14-.29.29'
           '-.12.57.17.28.74 1.22 1.59 1.98 1.09.97 2.01 1.27 2.29 1.41.28.14.45.12.62-.07.17-.19.71-.83.9-1.11.19-.28.38'
           '-.24.64-.14.26.09 1.65.78 1.94.92.28.14.47.21.54.33.07.11.07.65-.17 1.33Z"/></svg>')

ICO_INSTA = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
             '<path d="M12 4.14c2.56 0 2.87.01 3.88.06.94.04 1.44.2 1.78.33.45.17.77.38 1.1.72.34.33.55.65.72 1.1.13.34.29.84.33 1.78'
             '.05 1.01.06 1.32.06 3.88s-.01 2.87-.06 3.88c-.04.94-.2 1.44-.33 1.78-.17.45-.38.77-.72 1.1-.33.34-.65.55-1.1.72'
             '-.34.13-.84.29-1.78.33-1.01.05-1.32.06-3.88.06s-2.87-.01-3.88-.06c-.94-.04-1.44-.2-1.78-.33a2.96 2.96 0 0 1-1.1-.72'
             # O 'a' desta linha se perdeu na quebra: sem ele o navegador lia
             # "-.723 3 0 0 1" e abandonava o path inteiro — o ícone do
             # Instagram não desenhava, com seis erros no console.
             'a3 3 0 0 1-.72-1.1c-.13-.34-.29-.84-.33-1.78C4.15 14.87 4.14 14.56 4.14 12s.01-2.87.06-3.88c.04-.94.2-1.44.33-1.78'
             '.17-.45.38-.77.72-1.1.33-.34.65-.55 1.1-.72.34-.13.84-.29 1.78-.33 1.01-.05 1.32-.06 3.88-.06Z"/>'
             '<path d="M12 7.19a4.81 4.81 0 1 0 0 9.62 4.81 4.81 0 0 0 0-9.62Zm0 7.93a3.12 3.12 0 1 1 0-6.24 3.12 3.12 0 0 1 0 6.24Z" class="ico-vazado"/>'
             '<circle cx="17.1" cy="6.9" r="1.13" class="ico-vazado"/></svg>')

ICO_MAPA_CHEIO = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Z'
                  'm0-8.6a2.6 2.6 0 1 1 0-5.2 2.6 2.6 0 0 1 0 5.2Z"/></svg>')

ICO_ESTRELA = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
               '<path d="m12 2.6 2.9 5.9 6.5.9-4.7 4.6 1.1 6.5-5.8-3-5.8 3 1.1-6.5L2.6 9.4l6.5-.9L12 2.6Z"/></svg>')

SETA = ('<svg class="seta" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" '
        'aria-hidden="true" focusable="false"><path d="M4 12h15m0 0-5.5-5.5M19 12l-5.5 5.5" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>')

SETA_GRANDE = ('<svg class="indice__seta" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1" '
               'aria-hidden="true" focusable="false"><path d="M7 16h18m0 0-7-7m7 7-7 7" '
               'stroke-linecap="round" stroke-linejoin="round"/></svg>')

FECHAR = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
          '<path d="M6 6l12 12M18 6 6 18" stroke-linecap="round"/></svg>')

TRACOS = {
    "pino": '<path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Z" stroke-linejoin="round"/><circle cx="12" cy="10" r="2.6"/>',
    "relogio": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.2V12l3.2 2" stroke-linecap="round"/>',
    "fone": '<path d="M6.3 3.8h3.1l1.6 4-2 1.3a12 12 0 0 0 5.9 5.9l1.3-2 4 1.6v3.1a1.8 1.8 0 0 1-2 1.8A16.4 16.4 0 0 1 4.5 5.8a1.8 1.8 0 0 1 1.8-2Z" stroke-linejoin="round"/>',
    "insta": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17" cy="7" r="1" fill="currentColor" stroke="none"/>',
}


def icone(nome):
    t = TRACOS.get(nome)
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.15" '
            'aria-hidden="true" focusable="false">%s</svg>' % t) if t else ""


def estrelas():
    return '<span class="estrelas" aria-hidden="true">%s</span>' % (ICO_ESTRELA * 5)


# ---------------------------------------------------------------------------
# Campo de fotografia
# ---------------------------------------------------------------------------

EXTENSOES = (".avif", ".webp", ".jpg", ".jpeg", ".png")
CAMPOS = []

# Ficha de cada fotografia, vinda do dados.json e indexada pelo id do campo:
#   alt   texto alternativo real da imagem, no lugar do genérico da seção
#   foco  object-position, para o recorte cair no lugar certo
# Existe porque o mesmo arquivo é cortado em proporções muito diferentes — um
# retrato 2:3 vira quase quadrado no painel e uma faixa 2,45:1 na banda do
# modal. No centro, o corte decepa cabeça. Aqui se diz onde está o assunto.
FICHAS = D.get("fotos", {})


def arquivo_de_foto(id_foto):
    for ext in EXTENSOES:
        rel = "assets/img/fotos/%s%s" % (id_foto, ext)
        if os.path.exists(os.path.join(RAIZ, rel)):
            return rel
    return None


def campo(id_foto, alt, classe="campo", onde="", parallax=None, prioritaria=False):
    """Espaço de fotografia. Enquanto não houver arquivo o campo fica EM BRANCO
    — uma superfície um tom fora do fundo, com filete. Nada de monograma, nada
    de banco de imagens. Para preencher, salve a imagem em
    assets/img/fotos/<id> e rode o gerador de novo; o alt e o enquadramento
    saem da seção `fotos` do dados.json."""
    arquivo = arquivo_de_foto(id_foto)
    ficha = FICHAS.get(id_foto) or {}
    # O alt genérico da seção só vale enquanto ninguém descreveu a imagem de
    # verdade. Descrito, o específico ganha — é ele que o leitor de tela ouve.
    alt = ficha.get("alt") or alt
    CAMPOS.append((id_foto, onde, alt, arquivo))
    par = ' data-parallax="%s"' % parallax if (parallax and arquivo) else ""
    foco = ' style="object-position:%s"' % e(ficha["foco"]) if ficha.get("foco") else ""
    if arquivo:
        carga = ('loading="eager" fetchpriority="high"' if prioritaria else 'loading="lazy"')
        return ('<div class="%s campo--real" data-campo="%s">'
                '<img src="%s" alt="%s" %s decoding="async"%s%s></div>'
                % (classe, e(id_foto), e(arquivo), e(alt), carga, par, foco))
    # Sem imagem o campo é decorativo: aria-hidden evita que o leitor de tela
    # anuncie uma fotografia que não existe.
    return ('<!-- CAMPO DE FOTO [%s]: %s -->'
            '<div class="%s" data-campo="%s" aria-hidden="true"></div>'
            % (e(id_foto), e(alt), classe, e(id_foto)))


# ---------------------------------------------------------------------------
# Dados estruturados
# ---------------------------------------------------------------------------

def schema():
    horas = [{"@type": "OpeningHoursSpecification", "dayOfWeek": h["schema"],
              "opens": h["abre"], "closes": h["fecha"]}
             for h in C["horarios"] if h["abre"]]
    negocio = {
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
        "address": {"@type": "PostalAddress", "streetAddress": C["endereco_rua"],
                    "addressLocality": C["cidade"], "addressRegion": C["uf"],
                    "postalCode": C["endereco_cep"], "addressCountry": "BR"},
        "areaServed": {"@type": "City", "name": C["cidade"]},
        "openingHoursSpecification": horas,
        "sameAs": [C["instagram_url"]],
        "hasMap": maps_url(),
        "aggregateRating": {"@type": "AggregateRating",
                            "ratingValue": C["google_nota"].replace(",", "."),
                            "reviewCount": C["google_avaliacoes"], "bestRating": "5"},
    }
    servicos = [{
        "@type": "Service", "name": cat["nome"], "description": cat["resumo"],
        "url": SITE + "/#modal-" + cat["slug"],
        "provider": {"@id": SITE + "/#negocio"},
        "areaServed": {"@type": "City", "name": C["cidade"]},
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": cat["nome"], "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": p["nome"],
                                               "description": p["resumo"]}}
            for p in cat["procedimentos"]]},
    } for cat in CATS]
    servicos.append({
        "@type": "Service", "name": "Dia da Noiva",
        "description": D["noivas"]["texto"],
        "url": SITE + "/#modal-noivas",
        "provider": {"@id": SITE + "/#negocio"},
        "areaServed": {"@type": "City", "name": C["cidade"]},
    })
    pessoas = [{"@type": "Person", "name": m["nome"], "jobTitle": m["papel"],
                "worksFor": {"@id": SITE + "/#negocio"},
                **({"sameAs": [m["instagram_url"]]} if m.get("instagram_url") else {})}
               for m in D["equipe"]]
    faq = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q["p"],
         "acceptedAnswer": {"@type": "Answer", "text": q["r"]}} for q in D["faq"]]}
    site = {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/",
            "name": C["nome"], "inLanguage": "pt-BR",
            "publisher": {"@id": SITE + "/#negocio"}}
    grafo = {"@context": "https://schema.org", "@graph": [negocio, site, faq] + servicos + pessoas}
    corpo = json.dumps(grafo, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return '<script type="application/ld+json">%s</script>' % corpo


# ---------------------------------------------------------------------------
# Esqueleto
# ---------------------------------------------------------------------------

def cabeca(titulo=None, desc=None, caminho="", robots="index, follow, max-image-preview:large",
           com_schema=True):
    titulo = titulo or "%s — Estética avançada e salão de beleza em %s" % (C["nome"], C["cidade"])
    desc = desc or ("Clínica de estética avançada e salão de beleza em Londrina. Pele, cabelo, unhas, "
                    "sobrancelhas, maquiagem e Dia da Noiva no mesmo endereço. Agende pelo WhatsApp.")
    return """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titulo)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(site)s/%(caminho)s">
<meta name="theme-color" content="#faf6f2">
<meta name="robots" content="%(robots)s">
<meta name="geo.region" content="BR-%(uf)s">
<meta name="geo.placename" content="%(cidade)s">

<meta property="og:type" content="website">
<meta property="og:site_name" content="%(nome)s">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="%(titulo)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(site)s/%(caminho)s">
<meta property="og:image" content="%(site)s/assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="%(nome)s — %(ass)s em %(cidade)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(titulo)s">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="%(site)s/assets/img/og.png">

<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/img/favicon.svg">

<link rel="preload" href="assets/fonts/cormorant-latin-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/cormorant-italic-latin-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/jost-latin-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/js/vendor/lenis.css?v=%(v)s">
<link rel="stylesheet" href="assets/css/helenas.css?v=%(v)s">

<script>
/* Esconder-para-animar acontece aqui, antes da primeira pintura, para não
   haver piscada — e só onde a animação vai existir. Se o app.js não confirmar
   que subiu em 4 segundos (rede ruim, arquivo bloqueado, erro de script), a
   classe cai sozinha e a página aparece inteira. Nenhum conteúdo depende de
   JavaScript para ser visto. */
(function () {
  var d = document.documentElement;
  if (!window.matchMedia || !matchMedia('(prefers-reduced-motion: no-preference)').matches) return;
  d.classList.add('js');
  setTimeout(function () { if (!window.__helenasOk) d.classList.remove('js'); }, 4000);
})();
</script>
%(schema)s
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
""" % {"titulo": e(titulo), "desc": e(desc), "site": e(SITE), "nome": e(C["nome"]),
       "ass": e(C["assinatura"]), "cidade": e(C["cidade"]), "uf": e(C["uf"]),
       "v": V, "caminho": e(caminho), "robots": e(robots),
       "schema": schema() if com_schema else ""}


def marca(tag="a", href="#inicio"):
    atr = ' href="%s"' % href if tag == "a" else ""
    return ('<%(t)s class="marca"%(a)s><span class="marca__selo" aria-hidden="true">ch</span>'
            '<span class="marca__texto"><span class="marca__nome">%(n)s</span>'
            '<span class="marca__assinatura">%(s)s</span></span></%(t)s>'
            % {"t": tag, "a": atr, "n": e(C["marca"]), "s": e(C["assinatura"])})


def topo():
    links = "".join('<a class="topo__link" href="#%s">%s</a>' % (n["id"], e(n["rotulo"]))
                    for n in D["navegacao"])
    gaveta = "".join('<a href="#%s">%s<span>%02d</span></a>' % (n["id"], e(n["rotulo"]), i + 1)
                     for i, n in enumerate(D["navegacao"]))
    return """<header class="topo" data-topo>
<div class="env topo__barra">
%(marca)s
<nav class="topo__nav" aria-label="Seções da página">%(links)s</nav>
<a class="botao botao--primario topo__acao" href="%(zap)s" target="_blank" rel="noopener">Agendar</a>
<button class="menu-botao" type="button" data-menu-botao aria-expanded="false" aria-controls="gaveta">
<span class="menu-botao__traco" aria-hidden="true"><span></span><span></span><span></span></span>Menu</button>
</div>
</header>
<div class="gaveta" id="gaveta" data-gaveta data-aberta="nao" data-lenis-prevent>
<nav class="gaveta__lista" aria-label="Seções da página">%(gaveta)s</nav>
<div class="gaveta__rodape">
<a class="botao botao--primario" href="%(zap)s" target="_blank" rel="noopener">%(ico)s Agendar pelo WhatsApp</a>
<p class="gaveta__contato"><span>%(tel)s</span><span>%(hor)s</span></p>
</div>
</div>
<div class="trilho" data-trilho data-visivel="nao" aria-hidden="true">
<span class="trilho__preenche" data-trilho-preenche></span>
</div>
""" % {"marca": marca(), "links": links, "gaveta": gaveta, "zap": e(zap(W["agendar"])),
       "ico": ICO_ZAP, "tel": e(C["whatsapp_exibicao"]), "hor": e(C["horario_curto"])}


# ---------------------------------------------------------------------------
# Atos
# ---------------------------------------------------------------------------

def ato_hero():
    h = D["hero"]
    linhas = ""
    for i, txt in enumerate(h["titulo_linhas"]):
        cls = ' class="italico"' if i >= h["linha_italica"] - 1 else ""
        linhas += '<span class="linha"><span%s>%s</span></span>' % (cls, e(txt))
    return """<section class="hero" id="inicio" aria-labelledby="t-hero">
<div class="env hero__grade">
<div>
<p class="etiqueta" data-fx="etiqueta">%(etiq)s</p>
<h1 class="hero__titulo" id="t-hero">%(linhas)s</h1>
<p class="hero__texto" data-fx>%(texto)s</p>
<div class="hero__acoes" data-fx>
<a class="botao botao--primario" href="%(zap)s" target="_blank" rel="noopener">%(ico)s %(cta)s</a>
<a class="botao botao--contorno" href="#a-casa">%(cta2)s</a>
</div>
<div class="hero__nota" data-fx>
<span>%(estrelas)s <strong>%(nota)s</strong> em %(qtd)s avaliações no Google</span>
</div>
</div>
<div class="hero__placa" data-fx>%(campo)s</div>
</div>
<div class="env hero__rodape">
<span>%(esq)s</span>
<span class="hero__rolar">%(rolar)s</span>
<span>%(dir)s</span>
</div>
</section>
""" % {"etiq": e(h["etiqueta"]), "linhas": linhas, "texto": e(h["texto"]),
       "zap": e(zap(W["agendar"])), "ico": ICO_ZAP, "cta": e(h["cta"]), "cta2": e(h["cta2"]),
       "estrelas": estrelas(), "nota": e(C["google_nota"]), "qtd": C["google_avaliacoes"],
       # Eager e prioridade alta: no desktop esta é a imagem da primeira tela.
       # Atenção ao custo no celular: a .hero__placa é display:none abaixo de
       # 62rem, e o navegador baixa a foto mesmo assim — medido, e também em
       # loading="lazy", que não evita o download de um <img> sem caixa. São
       # ~85 KB que o celular paga por uma imagem que não vê. A saída real é
       # decidir se a placa deve aparecer no celular; enquanto não aparece, o
       # eager pelo menos rende no desktop.
       "campo": campo("hero", "Recepção da Clínica Helenas", "campo", "Hero — placa vertical do topo", prioritaria=True),
       "esq": e(h["rodape_esquerda"]), "rolar": e(h["rolar"]), "dir": e(h["rodape_direita"])}


def ato_manifesto():
    m = D["manifesto"]
    paras = "".join('<p data-fx>%s</p>' % e(p) for p in m["paragrafos"])
    return """<section class="ato" id="manifesto" aria-labelledby="t-manifesto">
<div class="env manifesto__grade">
<div class="manifesto__titulo">
<p class="etiqueta" data-fx="etiqueta">%(etiq)s</p>
<h2 id="t-manifesto" data-fx="titulo">%(titulo)s</h2>
</div>
<div class="manifesto__corpo">%(paras)s
<div class="assinatura" data-fx>
<span class="assinatura__nome">%(nome)s</span>
<span class="assinatura__papel">%(papel)s</span>
</div>
</div>
</div>
</section>
""" % {"etiq": e(m["etiqueta"]), "titulo": e(m["titulo"]), "paras": paras,
       "nome": e(m["assinatura"]), "papel": e(m["assinatura_papel"])}


def ato_casa():
    k = D["casa"]
    paineis = ""
    for i, p in enumerate(k["paineis"]):
        marcadores = "".join("<li>%s</li>" % e(x) for x in p["marcadores"])
        paineis += """<article class="painel" data-painel>
<div class="painel__grade">
<div class="painel__texto">
<span class="painel__ordem" aria-hidden="true">%(ord)s</span>
<p class="painel__etiqueta">%(etiq)s</p>
<h3>%(titulo)s</h3>
<p>%(texto)s</p>
<ul class="painel__marcadores">%(marc)s</ul>
</div>
<div class="painel__campo">%(campo)s</div>
</div>
</article>""" % {"ord": e(p["ordem"]), "etiq": e(p["etiqueta"]), "titulo": e(p["titulo"]),
                 "texto": e(p["texto"]), "marc": marcadores,
                 "campo": campo("casa-%d" % (i + 1), "Ambiente da Clínica Helenas: %s" % p["titulo"],
                                "campo", "A casa — painel %d (%s)" % (i + 1, p["titulo"]))}
    return """<section class="ato casa ato--sobe" id="a-casa" data-tema="escuro" data-pin="pilha" aria-labelledby="t-casa">
<div class="env">
<div class="casa__cabeca">
<p class="etiqueta" data-fx="etiqueta">%(etiq)s</p>
<h2 id="t-casa" data-fx="titulo">%(titulo)s</h2>
<p class="texto-g" data-fx>%(texto)s</p>
</div>
<div class="casa__palco" data-palco>%(paineis)s</div>
</div>
</section>
""" % {"etiq": e(k["etiqueta"]), "titulo": e(k["titulo"]), "texto": e(k["texto"]), "paineis": paineis}


def ato_numeros():
    n = D["numeros"]
    itens = "".join(
        '<div class="numero" data-fx><span class="numero__valor">%s</span>'
        '<span class="numero__rotulo">%s</span><span class="numero__detalhe">%s</span></div>'
        % (e(x["valor"]), e(x["rotulo"]), e(x["detalhe"])) for x in n["itens"])
    return """<section class="ato ato--curto" id="numeros" aria-labelledby="t-numeros">
<div class="env">
<div class="casa__cabeca">
<p class="etiqueta" data-fx="etiqueta">%(etiq)s</p>
<h2 id="t-numeros" data-fx="titulo">%(titulo)s</h2>
</div>
<div class="numeros__grade">%(itens)s</div>
</div>
</section>
""" % {"etiq": e(n["etiqueta"]), "titulo": e(n["titulo"]), "itens": itens}


def ato_tratamentos():
    t = D["tratamentos"]
    linhas = ""
    for i, cat in enumerate(CATS, 1):
        linhas += """<li class="indice__item" data-fx>
<button class="indice__botao" type="button" data-abre="modal-%(slug)s"
        aria-haspopup="dialog" aria-label="%(rotulo)s">
<span class="indice__ordem" aria-hidden="true">%(ord)02d</span>
<span class="indice__corpo">
<span class="indice__nome">%(nome)s</span>
<span class="indice__resumo">%(resumo)s</span>
<span class="indice__mais">%(abrir)s</span>
</span>
%(seta)s</button></li>""" % {"slug": cat["slug"], "ord": i, "nome": e(cat["nome"]),
                             "resumo": e(cat["resumo"]), "abrir": e(t["abrir"]), "seta": SETA_GRANDE,
                             "rotulo": e("%s — %s" % (t["abrir"], cat["nome"]))}
    return """<section class="ato ato--areia" id="tratamentos" aria-labelledby="t-trat">
<div class="env trat__grade">
<div class="trat__coluna">
<p class="etiqueta" data-fx="etiqueta">%(etiq)s</p>
<h2 id="t-trat" data-fx="titulo">%(titulo)s</h2>
<p data-fx>%(texto)s</p>
</div>
<ul class="indice">%(linhas)s</ul>
</div>
</section>
""" % {"etiq": e(t["etiqueta"]), "titulo": e(t["titulo"]), "texto": e(t["texto"]), "linhas": linhas}


def ato_noivas():
    n = D["noivas"]
    etapas = "".join(
        '<li class="etapa"><div><span class="etapa__quando">%s</span>'
        '<h3>%s</h3><p>%s</p></div></li>' % (e(x["quando"]), e(x["marco"]), e(x["texto"]))
        for x in n["cronograma"])
    return """<section class="ato noivas ato--sobe" id="noivas" data-tema="escuro" aria-labelledby="t-noivas">
<div class="env noivas__grade">
<div class="noivas__coluna">
<p class="etiqueta" data-fx="etiqueta">%(etiq)s</p>
<h2 id="t-noivas" data-fx="titulo">%(titulo)s</h2>
<p data-fx>%(texto)s</p>
<div data-fx><button class="botao botao--claro" type="button" data-abre="modal-noivas"
     aria-haspopup="dialog">%(abrir)s %(seta)s</button></div>
<div class="noivas__campo" data-fx>%(campo)s</div>
</div>
<ol class="cronograma">%(etapas)s</ol>
</div>
</section>
""" % {"etiq": e(n["etiqueta"]), "titulo": e(n["titulo"]), "texto": e(n["texto"]),
       "abrir": e(n["abrir"]), "seta": SETA, "etapas": etapas,
       "campo": campo("noiva", "Noiva sendo preparada na Clínica Helenas", "campo",
                      "Noivas — retrato vertical ao lado do cronograma")}


def ato_equipe():
    q = D["equipe_secao"]
    destaques = [m for m in D["equipe"] if m.get("destaque")]
    demais = [m for m in D["equipe"] if not m.get("destaque")]
    blocos = ""
    for m in destaques:
        areas = "".join('<span class="marca-area">%s</span>' % e(a) for a in m.get("areas", []))
        insta = ('<a class="link-filete" href="%s" target="_blank" rel="noopener">@%s %s</a>'
                 % (e(m["instagram_url"]), e(m["instagram_usuario"]), SETA)) if m.get("instagram_url") else ""
        mais = ('<button class="link-filete" type="button" data-abre="modal-%s" aria-haspopup="dialog">'
                'Conhecer %s %s</button>' % (apelido(m["nome"]), e(m["nome"].split()[0]), SETA)) if m.get("bio") else ""
        blocos += """<div class="perfil">
<div data-fx>%(campo)s</div>
<div class="perfil__texto">
<span class="perfil__papel" data-fx="etiqueta">%(papel)s</span>
<h3 data-fx="titulo" style="font-size:var(--t-h2)">%(nome)s</h3>
<div class="perfil__bio" data-fx><p>%(bio)s</p></div>
<div class="perfil__areas" data-fx>%(areas)s</div>
<div data-fx style="display:flex;gap:var(--e6);flex-wrap:wrap">%(mais)s%(insta)s</div>
</div>
</div>""" % {"campo": campo("equipe-" + apelido(m["nome"]), "Retrato de " + m["nome"],
                            "campo", "Equipe — retrato de " + m["nome"]),
             "papel": e(m["papel"]), "nome": e(m["nome"]),
             "bio": e(m["bio"][0]) if m.get("bio") else "", "areas": areas,
             "mais": mais, "insta": insta}

    grade = ""
    if demais:
        cartoes = "".join(
            '<article class="membro" data-fx>%s<div><span class="perfil__papel">%s</span>'
            '<h3 style="margin-top:var(--e2)">%s</h3></div>'
            '<div class="perfil__areas">%s</div></article>'
            % (campo("equipe-" + apelido(m["nome"]), "Retrato de " + m["nome"], "campo",
                     "Equipe — retrato de " + m["nome"]),
               e(m["papel"]), e(m["nome"]),
               "".join('<span class="marca-area">%s</span>' % e(a) for a in m.get("areas", [])))
            for m in demais)
        grade = '<div class="equipe__grade">%s</div>' % cartoes

    return """<section class="ato" id="equipe" aria-labelledby="t-equipe">
<div class="env">
<div class="casa__cabeca">
<p class="etiqueta" data-fx="etiqueta">%(etiq)s</p>
<h2 id="t-equipe" data-fx="titulo">%(titulo)s</h2>
<p class="texto-g" data-fx>%(texto)s</p>
</div>
%(blocos)s
%(grade)s
</div>
</section>
""" % {"etiq": e(q["etiqueta"]), "titulo": e(q["titulo"]), "texto": e(q["texto"]),
       "blocos": blocos, "grade": grade}


def ato_depoimentos():
    d = D["depoimentos"]
    itens = "".join(
        '<figure class="avaliacao" data-fx>%s<blockquote>%s</blockquote>'
        '<figcaption><strong>%s</strong><span>Avaliação no %s</span></figcaption></figure>'
        % (estrelas(), e(a["texto"]), e(a["autor"]), e(a["origem"])) for a in D["avaliacoes"])
    return """<section class="ato ato--veu" id="depoimentos" aria-labelledby="t-dep">
<div class="env dep__grade">
<div class="dep__coluna">
<p class="etiqueta" data-fx="etiqueta">%(etiq)s</p>
<h2 id="t-dep" data-fx="titulo">%(titulo)s</h2>
<p class="nota-google" data-fx>%(estrelas)s <span><strong>%(nota)s</strong> em %(qtd)s avaliações no Google</span></p>
</div>
<div class="dep__lista">%(itens)s</div>
</div>
</section>
""" % {"etiq": e(d["etiqueta"]), "titulo": e(d["titulo"]), "estrelas": estrelas(),
       "nota": e(C["google_nota"]), "qtd": C["google_avaliacoes"], "itens": itens}


def lista_faq(itens):
    return "".join(
        '<details class="faq__item"><summary>%s<span class="faq__sinal" aria-hidden="true"></span></summary>'
        '<div class="faq__resposta"><p>%s</p></div></details>' % (e(q["p"]), e(q["r"]))
        for q in itens)


def ato_duvidas():
    f = D["faq_secao"]
    return """<section class="ato" id="duvidas" aria-labelledby="t-faq">
<div class="env dep__grade">
<div class="dep__coluna">
<p class="etiqueta" data-fx="etiqueta">%(etiq)s</p>
<h2 id="t-faq" data-fx="titulo">%(titulo)s</h2>
<p data-fx>%(texto)s</p>
</div>
<div data-fx>%(itens)s</div>
</div>
</section>
""" % {"etiq": e(f["etiqueta"]), "titulo": e(f["titulo"]), "texto": e(f["texto"]),
       "itens": lista_faq(D["faq"])}


def formulario():
    opcoes = "".join('<option value="%s">%s</option>' % (e(c["nome"]), e(c["nome"])) for c in CATS)
    return """<form class="formulario" data-form="https://wa.me/%(num)s" novalidate>
<div class="campo-form">
<label for="f-nome">Seu nome</label>
<input id="f-nome" name="nome" type="text" required minlength="2" autocomplete="name"
       data-faltando="Diga como podemos te chamar.">
<span class="campo-form__erro" data-erro role="alert"></span>
</div>
<div class="campo-form">
<label for="f-tel">Telefone com DDD</label>
<input id="f-tel" name="telefone" type="tel" required minlength="8" autocomplete="tel"
       inputmode="tel" placeholder="(43) 90000-0000" data-faltando="Precisamos de um telefone para retornar.">
<span class="campo-form__erro" data-erro role="alert"></span>
</div>
<div class="campo-form">
<label for="f-assunto">Sobre o que você quer falar</label>
<select id="f-assunto" name="assunto">
<option value="">Escolha uma opção</option>%(opcoes)s
<option value="Dia da Noiva">Dia da Noiva</option>
<option value="Outro assunto">Outro assunto</option>
</select>
<span class="campo-form__erro" data-erro role="alert"></span>
</div>
<div class="campo-form">
<label for="f-msg">Mensagem (opcional)</label>
<textarea id="f-msg" name="mensagem" rows="3"
          placeholder="Conte o que você quer cuidar ou a data que tem em mente."></textarea>
<span class="campo-form__erro" data-erro role="alert"></span>
</div>
<p class="formulario__aviso" data-aviso hidden></p>
<button class="botao botao--primario" type="submit">%(ico)s Enviar pelo WhatsApp</button>
<p class="formulario__nota">Ao enviar, o formulário abre o WhatsApp com a sua mensagem já escrita.
Nada é armazenado neste site.</p>
</form>""" % {"num": e(C["whatsapp_numero"]), "opcoes": opcoes, "ico": ICO_ZAP}


def ato_visita():
    v = D["visita"]
    f = D["final"]
    horarios = "".join('<li><span>%s</span> <span>%s</span></li>' % (e(h["dias"]), e(h["texto"]))
                       for h in C["horarios"])
    return """<section class="ato visita" id="visita" aria-labelledby="t-visita">
<div class="env">
<div class="visita__cartao">
<div class="casa__cabeca">
<p class="etiqueta" data-fx="etiqueta">%(etiq)s</p>
<h2 id="t-visita" data-fx="titulo">%(titulo)s</h2>
<p class="texto-g" data-fx>%(texto)s</p>
</div>
<div class="visita__grade">
<div class="dados" data-fx>
<div class="dado">%(i_pino)s<div>
<span class="dado__rotulo">Endereço</span>
<a class="dado__valor" href="%(maps)s" target="_blank" rel="noopener">%(rua)s</a>
<p class="dado__extra">%(bairro)s · %(cidade)s/%(uf)s · CEP %(cep)s</p>
</div></div>
<div class="dado">%(i_fone)s<div>
<span class="dado__rotulo">Telefone e WhatsApp</span>
<a class="dado__valor" href="%(zap)s" target="_blank" rel="noopener">%(tel)s</a>
<p class="dado__extra">O agendamento é feito por aqui.</p>
</div></div>
<div class="dado">%(i_rel)s<div>
<span class="dado__rotulo">Horários</span>
<ul class="horarios" style="margin-top:var(--e2)">%(horarios)s</ul>
</div></div>
<div class="dado">%(i_ig)s<div>
<span class="dado__rotulo">Instagram</span>
<a class="dado__valor" href="%(ig)s" target="_blank" rel="noopener">@%(iguser)s</a>
<p class="dado__extra">O dia a dia da clínica e os trabalhos da equipe.</p>
</div></div>
</div>
<div data-fx>%(form)s</div>
</div>
<div class="mapa" data-mapa="%(embed)s" data-titulo="Mapa com a localização da %(nome)s"
     style="margin-top:var(--e7)"></div>
</div>
</div>
<div class="env final">
<div class="final__grade">
<p class="etiqueta etiqueta--solta" data-fx="etiqueta">%(f_etiq)s</p>
<h2 data-fx="titulo">%(f_titulo)s</h2>
<p class="texto-g" data-fx>%(f_texto)s</p>
<div class="final__acoes" data-fx>
<a class="botao botao--claro" href="%(zap_av)s" target="_blank" rel="noopener">%(ico)s %(f_cta)s</a>
<a class="botao botao--claro" href="%(ig)s" target="_blank" rel="noopener">Ver o Instagram</a>
</div>
</div>
</div>
</section>
""" % {"etiq": e(v["etiqueta"]), "titulo": e(v["titulo"]), "texto": e(v["texto"]),
       "i_pino": icone("pino"), "i_fone": icone("fone"), "i_rel": icone("relogio"), "i_ig": icone("insta"),
       "maps": e(maps_url()), "rua": e(C["endereco_rua"]), "bairro": e(C["bairro"]),
       "cidade": e(C["cidade"]), "uf": e(C["uf"]), "cep": e(C["endereco_cep"]),
       "zap": e(zap(W["agendar"])), "tel": e(C["whatsapp_exibicao"]), "horarios": horarios,
       "ig": e(C["instagram_url"]), "iguser": e(C["instagram_usuario"]),
       "form": formulario(), "embed": e(maps_embed()), "nome": e(C["nome"]),
       "f_etiq": e(f["etiqueta"]), "f_titulo": e(f["titulo"]), "f_texto": e(f["texto"]),
       "zap_av": e(zap(W["avaliacao"])), "ico": ICO_ZAP, "f_cta": e(f["cta"])}


def rodape():
    links = "".join('<li><a href="#%s">%s</a></li>' % (n["id"], e(n["rotulo"])) for n in D["navegacao"])
    horarios = "".join('<li><span>%s</span> <span>%s</span></li>' % (e(h["dias"]), e(h["texto"]))
                       for h in C["horarios"])
    return """<footer class="rodape">
<div class="env">
<div class="rodape__grade">
<div>%(marca)s<p class="rodape__sobre">%(lema)s</p></div>
<div><p class="rodape__titulo">Nesta página</p><ul class="rodape__lista">%(links)s</ul></div>
<div><p class="rodape__titulo">A casa</p>
<ul class="rodape__lista">
<li><a href="%(maps)s" target="_blank" rel="noopener">%(end)s</a></li>
<li><a href="tel:+%(num)s">%(tel)s</a></li>
<li><a href="%(ig)s" target="_blank" rel="noopener">@%(iguser)s</a></li>
</ul>
<ul class="horarios" style="margin-top:var(--e5)">%(horarios)s</ul>
</div>
</div>
<div class="rodape__fim">
<p>© %(ano)s %(legal)s · CNPJ %(cnpj)s ·
<button class="rodape__legal" type="button" data-abre="modal-privacidade"
        aria-haspopup="dialog">%(priv)s</button></p>
<div class="rodape__sociais">
<a href="%(ig)s" target="_blank" rel="noopener" aria-label="Instagram da %(nome)s">%(i_ig)s</a>
<a href="%(zap)s" target="_blank" rel="noopener" aria-label="WhatsApp da %(nome)s">%(i_zap)s</a>
<a href="%(maps)s" target="_blank" rel="noopener" aria-label="Como chegar até a %(nome)s">%(i_mapa)s</a>
</div>
</div>
</div>
</footer>
""" % {"marca": marca("div"), "lema": e(C["lema"]), "links": links, "maps": e(maps_url()),
       "end": e(C["endereco_rua"] + " — " + C["cidade"] + "/" + C["uf"]),
       "num": e(C["whatsapp_numero"]), "tel": e(C["whatsapp_exibicao"]),
       "ig": e(C["instagram_url"]), "iguser": e(C["instagram_usuario"]), "horarios": horarios,
       "ano": datetime.date.today().year, "legal": e(C["nome_legal"]), "cnpj": e(C["cnpj"]),
       "priv": e(D["privacidade"]["rotulo_rodape"]),
       "nome": e(C["nome"]), "i_ig": ICO_INSTA, "i_zap": ICO_ZAP, "i_mapa": ICO_MAPA_CHEIO,
       "zap": e(zap(W["conversar"]))}


# ---------------------------------------------------------------------------
# Modais
# ---------------------------------------------------------------------------

def modal(ident, etiqueta, titulo, corpo, cta_rotulo, cta_href, nota=""):
    return """<dialog class="modal" id="%(id)s" aria-labelledby="%(id)s-t">
<div class="modal__caixa">
<div class="modal__topo">
<span class="modal__etiqueta">%(etiq)s</span>
<button class="modal__fechar" type="button" data-fechar>%(x)s Fechar</button>
</div>
<div class="modal__corpo" data-lenis-prevent tabindex="0" aria-label="Conteúdo de %(titulo_txt)s">
<div class="modal__interno">
<div class="modal__cabeca"><h2 id="%(id)s-t">%(titulo)s</h2></div>
%(corpo)s
</div>
</div>
<div class="modal__acao">
<p>%(nota)s</p>
<a class="botao botao--primario" href="%(href)s" target="_blank" rel="noopener">%(ico)s %(cta)s</a>
</div>
</div>
</dialog>
""" % {"id": ident, "etiq": e(etiqueta), "titulo": e(titulo), "titulo_txt": e(titulo),
       "corpo": corpo, "nota": e(nota), "href": e(cta_href), "ico": ICO_ZAP,
       "cta": e(cta_rotulo), "x": FECHAR}


def modal_categoria(cat):
    linhas = ""
    for i, p in enumerate(cat["procedimentos"], 1):
        duracao = ('<p class="proc__duracao">%s Duração aproximada: %s</p>'
                   % (icone("relogio"), e(p["duracao"]))) if p.get("duracao") else ""
        linhas += """<li class="proc__item"><div class="proc__linha">
<span class="proc__ordem" aria-hidden="true">%(ord)02d</span>
<div class="proc__cabeca"><h3>%(nome)s</h3><p class="proc__resumo">%(resumo)s</p>%(dur)s</div>
<div class="proc__corpo"><p>%(detalhe)s</p>
<dl class="proc__indicacao"><dt>Para quem</dt><dd>%(ind)s</dd></dl>
<a class="link-filete" href="%(zap)s" target="_blank" rel="noopener">Perguntar sobre %(nome_l)s %(seta)s</a>
</div></div></li>""" % {"ord": i, "nome": e(p["nome"]), "resumo": e(p["resumo"]), "dur": duracao,
                        "detalhe": e(p["detalhe"]), "ind": e(p["indicacao"]),
                        "zap": e(zap_sobre(p["nome"], "procedimento")),
                        "nome_l": e(p["nome"].lower()), "seta": SETA}

    faq = ""
    if cat.get("faq"):
        faq = ('<div class="modal__sub"><h3>Sobre %s</h3><div>%s</div></div>'
               % (e(cat["nome"].lower()), lista_faq(cat["faq"])))

    corpo = """<p class="texto-g" style="max-width:62ch;margin-top:var(--e5)">%(desc)s</p>
<div class="modal__banda">%(campo)s</div>
<ul class="proc">%(linhas)s</ul>
%(faq)s""" % {"desc": e(cat["descricao"]),
              "campo": campo("trat-" + cat["slug"], "Atendimento de %s" % cat["nome"].lower(),
                             "campo campo--banda", "Modal de %s — banda de abertura" % cat["nome"]),
              "linhas": linhas, "faq": faq}

    return modal("modal-" + cat["slug"], cat["etiqueta"], cat["chamada"], corpo,
                 "Agendar avaliação", zap_sobre(cat["nome"]),
                 "A avaliação presencial é o que define o protocolo.")


def modal_noivas():
    n = D["noivas"]
    intro = "".join("<p>%s</p>" % e(x) for x in n["intro_paragrafos"])
    etapas = "".join(
        '<li class="etapa" style="border-color:var(--linha)"><div>'
        '<span class="etapa__quando" style="color:var(--rose-forte)">%s</span>'
        '<h3>%s</h3><p style="color:var(--tinta-suave)">%s</p></div></li>'
        % (e(x["quando"]), e(x["marco"]), e(x["texto"])) for x in n["cronograma"])
    inclui = "".join("<li>%s</li>" % e(x) for x in n["inclui"])
    corpo = """<div class="modal__sub" style="margin-top:var(--e6)">
<h3>%(i_tit)s</h3>
<div style="display:grid;gap:var(--e4);color:var(--tinta-suave);max-width:64ch">%(intro)s</div>
</div>
<div class="modal__banda">%(campo)s</div>
<div class="modal__sub">
<h3>%(c_tit)s</h3>
<p style="color:var(--tinta-clara);font-size:var(--t-mini);max-width:60ch">%(c_nota)s</p>
<ol class="cronograma" style="counter-reset:etapa">%(etapas)s</ol>
</div>
<div class="modal__sub">
<h3>%(inc_tit)s</h3>
<p style="color:var(--tinta-clara);font-size:var(--t-mini)">%(inc_nota)s</p>
<ul class="inclui">%(inclui)s</ul>
</div>
<div class="modal__sub">
<h3>%(ac_tit)s</h3>
<p style="color:var(--tinta-suave);max-width:62ch">%(ac_txt)s</p>
</div>""" % {"i_tit": e(n["intro_titulo"]), "intro": intro,
             "campo": campo("noivas-banda", "Noiva pronta após o Dia da Noiva",
                            "campo campo--banda", "Modal de noivas — banda de abertura"),
             "c_tit": e(n["cronograma_titulo"]), "c_nota": e(n["cronograma_nota"]), "etapas": etapas,
             "inc_tit": e(n["inclui_titulo"]), "inc_nota": e(n["inclui_nota"]), "inclui": inclui,
             "ac_tit": e(n["acompanhantes_titulo"]), "ac_txt": e(n["acompanhantes_texto"])}
    return modal("modal-noivas", n["etiqueta"], "Dia da Noiva", corpo,
                 n["cta_rotulo"], zap(W["noiva"]), n["cta_texto"])


def modal_pessoa(m):
    bio = "".join("<p>%s</p>" % e(x) for x in m["bio"])
    areas = "".join('<span class="marca-area">%s</span>' % e(a) for a in m.get("areas", []))
    insta = ('<p style="margin-top:var(--e5)"><a class="link-filete" href="%s" target="_blank" '
             'rel="noopener">@%s %s</a></p>' % (e(m["instagram_url"]), e(m["instagram_usuario"]), SETA)
             ) if m.get("instagram_url") else ""
    corpo = """<div class="modal__banda">%(campo)s</div>
<div style="display:grid;gap:var(--e4);color:var(--tinta-suave);max-width:64ch">%(bio)s</div>
<div class="perfil__areas" style="margin-top:var(--e6)">%(areas)s</div>%(insta)s""" % {
        "campo": campo("equipe-" + apelido(m["nome"]) + "-modal", "Retrato de " + m["nome"],
                       "campo campo--banda", "Modal de %s — banda de abertura" % m["nome"]),
        "bio": bio, "areas": areas, "insta": insta}
    return modal("modal-" + apelido(m["nome"]), m["papel"], m["nome"], corpo,
                 "Falar com a Helenas", zap(W["conversar"]),
                 "O agendamento é feito pelo WhatsApp da clínica.")


def modal_privacidade():
    """A V1 tinha uma página de privacidade; numa página única ela vira modal.
    O site coleta texto num formulário e embute um mapa do Google — duas coisas
    que precisam estar escritas em algum lugar, mesmo que o formulário não
    guarde nada."""
    v = D["privacidade"]
    secoes = ""
    for sec in v["secoes"]:
        paras = "".join('<p style="color:var(--tinta-suave)">%s</p>' % e(x) for x in sec["paragrafos"])
        marc = ("<ul class=\"inclui\" style=\"margin-top:var(--e4)\">%s</ul>"
                % "".join("<li>%s</li>" % e(x) for x in sec.get("marcadores", []))) if sec.get("marcadores") else ""
        secoes += ('<div class="modal__sub"><h3>%s</h3>'
                   '<div style="display:grid;gap:var(--e4);max-width:64ch">%s</div>%s</div>'
                   % (e(sec["titulo"]), paras, marc))

    corpo = ('<p class="texto-g" style="max-width:62ch;margin-top:var(--e5)">%s</p>'
             '%s'
             '<div class="modal__sub"><h3>%s</h3>'
             '<p style="color:var(--tinta-suave)">%s — CNPJ %s.<br>%s</p></div>'
             % (e(v["abertura"]), secoes, e(v["responsavel_titulo"]),
                e(C["nome_legal"]), e(C["cnpj"]), e(C["endereco_completo"])))

    return modal("modal-privacidade", v["etiqueta"], v["titulo"], corpo,
                 v["cta_rotulo"], zap(W["conversar"]), v["cta_nota"])


def modais():
    partes = [modal_categoria(c) for c in CATS]
    partes.append(modal_noivas())
    partes += [modal_pessoa(m) for m in D["equipe"] if m.get("bio")]
    partes.append(modal_privacidade())
    return "".join(partes)


def fim(com_movimento=True):
    """Fecha o documento. A 404 dispensa GSAP e Lenis: não tem seção pinada
    nem parallax. O app.js entra de qualquer forma — é ele que abre a gaveta,
    e a gaveta é a única navegação no celular."""
    libs = ""
    if com_movimento:
        libs = ('<script src="assets/js/vendor/gsap.min.js?v=%(v)s"></script>'
                '<script src="assets/js/vendor/ScrollTrigger.min.js?v=%(v)s"></script>'
                '<script src="assets/js/vendor/lenis.min.js?v=%(v)s"></script>' % {"v": V})
    return (libs + '<script src="assets/js/app.js?v=%s" defer></script>' % V
            + "</body>" + chr(10) + "</html>" + chr(10))


def flutuante():
    return ('<a class="zap" data-zap data-visivel="nao" href="%s" target="_blank" rel="noopener" '
            'aria-label="Falar com a %s pelo WhatsApp">%s</a>'
            % (e(zap(W["conversar"])), e(C["nome"]), ICO_ZAP))


# ---------------------------------------------------------------------------
# Página de endereço não encontrado
# ---------------------------------------------------------------------------

def pagina_404():
    """O GitHub Pages devolve esta página para qualquer endereço que não exista
    dentro do site — de /helenas/procedimentos (link antigo da V1) a um erro de
    digitação qualquer. Como o endereço falso pode ter qualquer profundidade,
    tudo aqui passa por absolutizar(). Ela não carrega GSAP nem Lenis: não tem
    seção pinada, e quem caiu num erro quer sair dele rápido."""
    atalhos = "".join(
        '<li class="indice__item"><a class="indice__botao" href="%s#%s">'
        '<span class="indice__ordem" aria-hidden="true">%02d</span>'
        '<span class="indice__corpo"><span class="indice__nome">%s</span></span>'
        '%s</a></li>' % (BASE, n["id"], i, e(n["rotulo"]), SETA_GRANDE)
        for i, n in enumerate(D["navegacao"], 1))

    corpo = u"""<section class="ato erro">
<div class="env erro__grade">
<span class="erro__codigo" aria-hidden="true">404</span>
<p class="etiqueta etiqueta--solta">Endereço não encontrado</p>
<h1>Esta página não existe</h1>
<p class="texto-g">Pode ser um link antigo ou um endereço digitado com alguma
diferença. A Helenas agora cabe numa página só — e ela está logo ali.</p>
<div class="erro__acoes">
<a class="botao botao--primario" href="%(base)s">Voltar ao início</a>
<a class="botao botao--contorno" href="%(zap)s" target="_blank" rel="noopener">Falar pelo WhatsApp</a>
</div>
</div>
</section>
<section class="ato ato--curto ato--areia">
<div class="env">
<p class="etiqueta etiqueta--solta" style="margin-bottom:var(--e5)">Os caminhos da casa</p>
<ul class="indice">%(atalhos)s</ul>
</div>
</section>
""" % {"base": e(BASE), "zap": e(zap(W["conversar"])), "atalhos": atalhos}

    partes = [
        absolutizar(cabeca(u"Página não encontrada — " + C["nome"],
                           u"Esta página não existe mais ou o endereço foi digitado com alguma "
                           u"diferença. Volte ao início do site da %s." % C["nome"],
                           caminho="404.html", robots="noindex, follow", com_schema=False),
                    ancoras=False),
        absolutizar(topo()),
        '<main id="conteudo">',
        corpo,
        "</main>",
        absolutizar(rodape()),
        modal_privacidade(),   # o rodape aponta para ele; sem isto, botão morto
        absolutizar(fim(com_movimento=False)),
    ]
    escrever("404.html", "".join(partes))


# ---------------------------------------------------------------------------
# Ativos gerados
# ---------------------------------------------------------------------------

def redirecionamentos():
    """A V1 tinha doze páginas com endereço próprio; a V3 tem uma só. Os dez
    endereços que continuam valendo ganham cada um uma página mínima que leva
    ao ponto equivalente da página única — /noivas/ abre o modal de noivas,
    /procedimentos/ cai na seção de tratamentos.

    Sem isto os dez caem na 404: o conteúdo existe, mas quem guardou o link
    não chega nele. O GitHub Pages não faz redirecionamento de servidor, então
    o instrumento é o meta refresh com atraso zero — que o Google trata como
    redirecionamento permanente — mais o location.replace para quem tem
    JavaScript, que evita empilhar uma entrada no histórico. O canonical
    aponta para a página única: é ele que junta num endereço só o que as dez
    páginas acumularam, em vez de jogar fora.

    O destino sai do `destino` de cada item em `redirecionamentos`, no
    dados.json. Apagar um item apaga a página na geração seguinte."""
    itens = D.get("redirecionamentos") or []
    for r in itens:
        alvo = BASE + r["destino"]          # /helenas/#modal-noivas
        pleno = SITE + "/"                  # canonical sem fragmento: o Google ignora
        escrever(r["de"].strip("/") + "/index.html",
                 '<!doctype html>\n<html lang="pt-BR">\n<head>\n'
                 '<meta charset="utf-8">\n'
                 '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                 '<title>%(t)s — %(nome)s</title>\n'
                 '<link rel="canonical" href="%(canon)s">\n'
                 '<meta http-equiv="refresh" content="0; url=%(alvo)s">\n'
                 '<script>location.replace(%(js)s);</script>\n'
                 '<style>body{font-family:system-ui,sans-serif;margin:3rem auto;'
                 'max-width:34rem;padding:0 1.5rem;color:#2c211d;background:#faf6f2;'
                 'line-height:1.6}a{color:#8a5a52}</style>\n'
                 '</head>\n<body>\n'
                 '<p>Esta página mudou de endereço.</p>\n'
                 '<p><a href="%(alvo)s">Continuar para %(t)s</a></p>\n'
                 '</body>\n</html>\n'
                 % {"t": e(r["titulo"]), "nome": e(C["nome"]), "canon": e(pleno),
                    "alvo": e(alvo), "js": json.dumps(alvo)})
    return len(itens)


def publicacao():
    """Arquivos que o GitHub Pages exige e que ninguém edita à mão.
    O .nojekyll é o mais importante dos três: sem ele o Jekyll ignora toda
    pasta e arquivo começado por sublinhado — e a pasta `_fonte` sumiria."""
    escrever(".nojekyll", "")
    linhas = ("* text=auto eol=lf", "*.woff2 binary", "*.png binary", "*.ico binary",
              "*.webp binary", "*.jpg binary", "*.jpeg binary", "*.avif binary")
    escrever(".gitattributes", "".join(l + "\n" for l in linhas))


def sitemap():
    escrever("sitemap.xml",
             '<?xml version="1.0" encoding="UTF-8"?>\n'
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
             '<url><loc>%s/</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>\n'
             '</urlset>\n' % SITE)


def robots():
    escrever("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)


def favicon_svg():
    escrever("assets/img/favicon.svg",
             '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
             '<rect width="64" height="64" rx="12" fill="#faf6f2"/>'
             '<circle cx="32" cy="32" r="25" fill="none" stroke="#b8807c" stroke-width="2.5"/>'
             '<text x="32" y="43" text-anchor="middle" font-family="Georgia,serif" '
             'font-size="30" fill="#8f5a56">ch</text></svg>\n')


def _png(largura, altura, linhas):
    def bloco(tipo, dados):
        c = tipo + dados
        return struct.pack(">I", len(dados)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    cru = b"".join(b"\x00" + linhas[y] for y in range(altura))
    return (b"\x89PNG\r\n\x1a\n"
            + bloco(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0))
            + bloco(b"IDAT", zlib.compress(cru, 9)) + bloco(b"IEND", b""))


def _cor(h):
    return bytes(int(h[i:i + 2], 16) for i in (0, 2, 4))


def favicon_ico():
    n = 32
    fundo, traco = _cor("faf6f2"), _cor("8f5a56")
    linhas = []
    for y in range(n):
        linha = bytearray()
        for x in range(n):
            d = ((x - 15.5) ** 2 + (y - 15.5) ** 2) ** 0.5
            linha += traco if 11.0 <= d <= 13.2 else fundo
        linhas.append(bytes(linha))
    png = _png(n, n, linhas)
    io.open(os.path.join(RAIZ, "favicon.ico"), "wb").write(
        struct.pack("<HHH", 0, 1, 1) + struct.pack("<BBBBHHII", n, n, 0, 0, 1, 32, len(png), 22) + png)


def og_imagem():
    L, A = 1200, 630
    marfim, ouro, rose = _cor("faf6f2"), _cor("b08d57"), _cor("e0c6bf")
    cx, cy = L / 2.0, A / 2.0
    linhas = []
    for y in range(A):
        linha = bytearray()
        for x in range(L):
            dv = ((x - L * 0.86) ** 2 + (y + A * 0.15) ** 2) ** 0.5
            base = rose if dv < 420 else marfim
            moldura = ((44 <= x <= L - 45 and 44 <= y <= A - 45) and not (46 <= x <= L - 47 and 46 <= y <= A - 47)) or \
                      ((56 <= x <= L - 57 and 56 <= y <= A - 57) and not (57 <= x <= L - 58 and 57 <= y <= A - 58))
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            linha += ouro if (moldura or 128.0 <= d <= 131.0) else base
        linhas.append(bytes(linha))
    io.open(os.path.join(RAIZ, "assets/img/og.png"), "wb").write(_png(L, A, linhas))


# ---------------------------------------------------------------------------
# Principal
# ---------------------------------------------------------------------------

def principal():
    partes = [
        cabeca(),
        topo(),
        '<main id="conteudo">',
        ato_hero(),
        ato_manifesto(),
        ato_casa(),
        ato_numeros(),
        ato_tratamentos(),
        ato_noivas(),
        ato_equipe(),
        ato_depoimentos(),
        ato_duvidas(),
        ato_visita(),
        "</main>",
        rodape(),
        modais(),
        flutuante(),
        fim(),
    ]
    escrever("index.html", "".join(partes))

    pagina_404()
    n_redir = redirecionamentos()
    publicacao()
    sitemap()
    robots()
    favicon_svg()
    favicon_ico()
    og_imagem()

    vistos = {}
    for ident, onde, alt, arq in CAMPOS:
        vistos.setdefault(ident, (onde, alt, arq))
    faltam = [i for i, (o, a, arq) in vistos.items() if not arq]
    escrever("_fonte/fotos-pendentes.txt",
             "Campos de fotografia do site.\n\n"
             "Para preencher um campo: salve o arquivo em assets/img/fotos/<id>.jpg\n"
             "(ou .webp, .avif, .png) e rode `python gerar.py`. O gerador troca o campo\n"
             "pela foto sozinho — não é preciso editar HTML. O texto alternativo e o\n"
             "enquadramento de cada uma saem da seção `fotos` do dados.json; sem ficha\n"
             "lá, a foto entra com o texto genérico da seção e recorte centralizado.\n\n"
             "Mínimo recomendado: 1400px no lado maior para retrato e painel,\n"
             "2400px de largura para as bandas de abertura dos modais (2,45:1).\n\n"
             "%d de %d preenchidos.\n\n" % (len(vistos) - len(faltam), len(vistos))
             + "\n".join("[%s] %-26s %s\n%33s alt: %s\n" % ("ok" if arq else "  ", i, o, "", a)
                         for i, (o, a, arq) in sorted(vistos.items())))

    tamanho = os.path.getsize(os.path.join(RAIZ, "index.html"))
    print("Página única gerada — %.0f KB de HTML. Versão dos ativos: %s" % (tamanho / 1024.0, V))
    print("%d modais, %d campos de fotografia (%d preenchidos)."
          % (len(CATS) + 2 + len([m for m in D["equipe"] if m.get("bio")]),
             len(vistos), len(vistos) - len(faltam)))
    print("%d endereços da V1 redirecionados para a página única." % n_redir)
    if D.get("_site_url_pendente"):
        print("Atenção: `site_url` ainda é provisório (%s)." % SITE)


if __name__ == "__main__":
    principal()
