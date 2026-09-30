# -*- coding: utf-8 -*-
"""
Verificador do site da Clínica Helenas.

Roda sobre o HTML já gerado e reclama do que um navegador não reclamaria:
link morto, âncora inexistente, título fora de tamanho, hierarquia de
cabeçalhos quebrada, imagem sem alternativa textual, link de WhatsApp com
número errado, marcador de pendência que vazou para o texto visível,
promessa de resultado e clichê de site de estética.

    python _fonte/verificar.py

Sai com código 1 se encontrar qualquer problema.
"""
import io
import json
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(io.open(os.path.join(RAIZ, "dados.json"), encoding="utf-8"))
NUMERO = D["clinica"]["whatsapp_numero"]

# Caminho do site na hospedagem — "/" num domínio próprio, "/helenas/" numa
# página de projeto do GitHub. A 404 usa links absolutos com esse prefixo, e
# em disco ele não existe: é preciso descontá-lo antes de procurar o arquivo.
BASE = (urlsplit(D["site_url"].rstrip("/")).path or "").rstrip("/") + "/"

# Clichês de site de estética. Os três primeiros são os que o briefing vetou
# por escrito; os demais são da mesma família.
CLICHES = [
    "transformando beleza em confiança",
    "sua melhor versão",
    "excelência, cuidado e inovação",
    "realçar sua beleza natural",
    "realçando sua beleza natural",
    "beleza que transforma",
    "sinta-se especial",
    "experiência única",
    "cuidar de você é nossa paixão",
    "resgate sua autoestima",
    "solução completa para",
    "o melhor de você",
    "beleza e bem-estar em harmonia",
]

# Nenhuma promessa de resultado: estética depende de pele, histórico e idade.
PROMESSAS = [
    "resultado garantido", "resultados garantidos", "garantimos o resultado",
    "garantia de resultado", "100% eficaz", "100% de eficácia",
    "sem dor", "efeito imediato e definitivo", "milagr", "rejuvenesce anos",
    "elimina definitivamente", "acaba com a flacidez", "perda de peso garantida",
]

# Marcador de pendência que não pode chegar ao texto visível. Sensível a caixa
# de propósito: "todo mundo" é português comum, "TODO" é marcador.
MARCADORES = [
    "TODO", "FIXME", "XXX", "TBD", "lorem ipsum", "{assunto}", "[inserir",
    "PENDENTE", "preencher aqui", "xxxxx",
]

TAM_TITULO = (15, 70)
TAM_DESCRICAO = (70, 170)


class Pagina(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titulo = None
        self.em_titulo = False
        self.metas = {}
        self.canonica = None
        self.links = []          # (href, tem_texto)
        self.ids = []
        self.cabecalhos = []     # (nivel, texto)
        self.nivel_atual = None
        self.texto_cab = ""
        self.sem_alt = []
        self.texto = []
        self.pilha_texto = []    # tags cujo conteúdo não é texto visível
        self.iframes_sem_titulo = 0
        self.botoes_sem_nome = 0
        self.lang = None

    # -- estrutura ---------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self.em_titulo = True
        if tag in ("script", "style"):
            self.pilha_texto.append(tag)
        if tag == "meta":
            chave = a.get("name") or a.get("property")
            if chave:
                self.metas[chave] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonica = a.get("href")
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append((a["href"], bool(a.get("aria-label"))))
        if tag == "img" and not a.get("alt") and a.get("alt") != "":
            self.sem_alt.append(a.get("src", "?"))
        if a.get("role") == "img" and not a.get("aria-label"):
            self.sem_alt.append("role=img sem aria-label")
        if tag == "iframe" and not a.get("title"):
            self.iframes_sem_titulo += 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.nivel_atual = int(tag[1])
            self.texto_cab = ""

    def handle_endtag(self, tag):
        if tag == "title":
            self.em_titulo = False
        if tag in ("script", "style") and self.pilha_texto:
            self.pilha_texto.pop()
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self.nivel_atual:
            self.cabecalhos.append((self.nivel_atual, self.texto_cab.strip()))
            self.nivel_atual = None

    def handle_data(self, dado):
        if self.em_titulo:
            self.titulo = (self.titulo or "") + dado
        if self.pilha_texto:
            return
        if self.nivel_atual:
            self.texto_cab += dado
        self.texto.append(dado)

    @property
    def texto_visivel(self):
        return re.sub(r"\s+", " ", "".join(self.texto))


def paginas():
    achadas = []
    for pasta, subpastas, arquivos in os.walk(RAIZ):
        subpastas[:] = [s for s in subpastas if s not in ("_fonte", "assets", ".git")]
        for arq in arquivos:
            if arq.endswith(".html") and not arq.startswith("_"):
                achadas.append(os.path.join(pasta, arq))
    return sorted(achadas)


def caminho_de_url(href, origem):
    """Resolve um href relativo para um caminho de arquivo em disco."""
    partes = urlsplit(href)
    caminho = unquote(partes.path)
    if BASE != "/" and caminho.startswith(BASE):
        caminho = "/" + caminho[len(BASE):]
    base = RAIZ if caminho.startswith("/") else os.path.dirname(origem)
    alvo = os.path.normpath(os.path.join(base, caminho.lstrip("/")))
    if os.path.isdir(alvo):
        alvo = os.path.join(alvo, "index.html")
    return alvo, partes.fragment


def principal():
    problemas = []
    ancoras = {}
    docs = {}

    for caminho in paginas():
        p = Pagina()
        p.feed(io.open(caminho, encoding="utf-8").read())
        docs[caminho] = p
        ancoras[os.path.normpath(caminho)] = set(p.ids)

    for caminho, p in docs.items():
        rel = os.path.relpath(caminho, RAIZ).replace("\\", "/")

        def erro(msg):
            problemas.append("%s: %s" % (rel, msg))

        # -- metadados -----------------------------------------------------
        if p.lang != "pt-BR":
            erro("atributo lang ausente ou diferente de pt-BR")
        if not p.titulo:
            erro("sem <title>")
        elif not (TAM_TITULO[0] <= len(p.titulo.strip()) <= TAM_TITULO[1]):
            erro("title com %d caracteres (esperado %d a %d): %r"
                 % (len(p.titulo.strip()), TAM_TITULO[0], TAM_TITULO[1], p.titulo.strip()))

        desc = p.metas.get("description", "")
        if not desc:
            erro("sem meta description")
        elif not (TAM_DESCRICAO[0] <= len(desc) <= TAM_DESCRICAO[1]):
            erro("meta description com %d caracteres (esperado %d a %d)"
                 % (len(desc), TAM_DESCRICAO[0], TAM_DESCRICAO[1]))

        if not p.canonica:
            erro("sem link canonical")
        for obrigatoria in ("og:title", "og:description", "og:image", "og:url"):
            if obrigatoria not in p.metas:
                erro("sem %s" % obrigatoria)

        # -- cabeçalhos ----------------------------------------------------
        h1s = [t for n, t in p.cabecalhos if n == 1]
        if len(h1s) != 1:
            erro("esperado exatamente 1 <h1>, encontrados %d" % len(h1s))
        anterior = 0
        for nivel, texto in p.cabecalhos:
            if anterior and nivel > anterior + 1:
                erro("salto de h%d para h%d em %r" % (anterior, nivel, texto[:40]))
            anterior = nivel
            if not texto:
                erro("cabeçalho h%d vazio" % nivel)

        # -- ids duplicados ------------------------------------------------
        vistos = set()
        for i in p.ids:
            if i in vistos:
                erro("id duplicado: %s" % i)
            vistos.add(i)

        # -- alternativas textuais ----------------------------------------
        for falta in p.sem_alt:
            erro("imagem sem alternativa textual: %s" % falta)
        if p.iframes_sem_titulo:
            erro("%d iframe(s) sem title" % p.iframes_sem_titulo)

        # -- links ---------------------------------------------------------
        for href, _ in p.links:
            if href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            if href.startswith("#"):
                if href[1:] and href[1:] not in p.ids:
                    erro("âncora inexistente nesta página: %s" % href)
                continue
            if href.startswith(("http://", "https://")):
                if "wa.me" in href:
                    if "/%s" % NUMERO not in href:
                        erro("link de WhatsApp com número diferente do dados.json: %s" % href[:70])
                    if "?text=" not in href:
                        erro("link de WhatsApp sem mensagem pré-escrita: %s" % href[:70])
                continue
            alvo, fragmento = caminho_de_url(href, caminho)
            if not os.path.exists(alvo):
                erro("link morto: %s" % href)
            elif fragmento:
                if fragmento not in ancoras.get(os.path.normpath(alvo), set()):
                    erro("âncora inexistente em %s: #%s" % (href, fragmento))

        # -- texto visível --------------------------------------------------
        visivel = p.texto_visivel
        minusculo = visivel.lower()
        for marca in MARCADORES:
            achado = visivel if marca.isupper() else minusculo
            if marca.lower() in achado.lower() and (marca in visivel if marca.isupper() else True):
                erro("marcador de pendência no texto visível: %r" % marca)
        for cliche in CLICHES:
            if cliche in minusculo:
                erro("clichê vetado no texto: %r" % cliche)
        for promessa in PROMESSAS:
            if promessa in minusculo:
                erro("promessa de resultado no texto: %r" % promessa)

    # -- ativos referenciados ------------------------------------------------
    for ativo in ("assets/css/helenas.css", "assets/js/helenas.js", "assets/img/og.png",
                  "assets/img/favicon.svg", "favicon.ico", "sitemap.xml", "robots.txt",
                  "assets/fonts/cormorant-latin-var.woff2",
                  "assets/fonts/cormorant-italic-latin-var.woff2",
                  "assets/fonts/jost-latin-var.woff2"):
        if not os.path.exists(os.path.join(RAIZ, ativo)):
            problemas.append("ativo ausente: %s" % ativo)

    # -- sitemap cobre as páginas publicadas ---------------------------------
    mapa = io.open(os.path.join(RAIZ, "sitemap.xml"), encoding="utf-8").read()
    for caminho in docs:
        rel = os.path.relpath(caminho, RAIZ).replace("\\", "/")
        if rel == "404.html":
            continue
        esperado = "" if rel == "index.html" else rel.replace("index.html", "")
        if ("/%s<" % esperado) not in mapa and not mapa.count(esperado):
            problemas.append("sitemap não lista %s" % rel)

    print("%d páginas verificadas." % len(docs))
    if problemas:
        print("\n%d problema(s):\n" % len(problemas))
        for x in problemas:
            print("  - " + x)
        return 1
    print("Nenhum problema encontrado.")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
