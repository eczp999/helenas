# Site da Clínica Helenas — V3, página única

Estética avançada e salão de beleza em Londrina/PR, com o Dia da Noiva como
especialidade da casa.

Esta é a **V3**: a V2 com a seção pinada consertada, três defeitos de
renderização resolvidos e fotografia nos espaços que estavam em branco. A V2
fica em `../v2` e a V1 — doze páginas separadas, no ar em
`https://eczp999.github.io/helenas/` — em `../v1`. As três leem o mesmo tipo
de arquivo de conteúdo e usam o mesmo gerador em Python puro: sem Node, sem
framework, sem build de JavaScript.

---

## O que mudou da V2 para a V3

| | V2 | V3 |
|---|---|---|
| Seção A Clínica | 1471px de altura numa tela de 900 | cabe em 100svh, os três painéis inteiros |
| `<h1>` do topo | nunca desenhava, em resolução nenhuma | aparece |
| Ícone do Instagram | `path` inválido, 6 erros no console | desenha |
| Fotografia | 15 espaços em branco | 11 preenchidos, em WebP |

A correção da seção A Clínica é a de fundo: a seção pinada media 571px a mais
que a tela, então o painel ficava com 40% da fotografia e metade do texto
abaixo da dobra — e o conteúdo só aparecia inteiro quando o pin soltava, no
terceiro painel. Agora a seção é uma grade de duas faixas dentro de 100svh e
tudo o que ocupa altura é medido em `vh`, não em `vw`.

O `<h1>` sumia por uma armadilha do GSAP: o CSS esconde as linhas com
`translateY(101%)`, o GSAP decompõe esse transform numa matriz — onde não
existe porcentagem — e o 101% vira `y = 101.757px`. Animar só `yPercent` de
101 a 0 deixava o pixel de pé, e o título terminava uma linha inteira abaixo
do invólucro que corta. A correção é declarar `y: 0` nos dois extremos.

## O que mudou da V1 para a V2

| | V1 | V2 |
|---|---|---|
| Estrutura | 12 páginas | 1 página + 6 modais |
| Navegação | links entre pastas | âncoras e rolagem conduzida |
| Movimento | transições simples | GSAP + ScrollTrigger + Lenis |
| Procedimentos | uma página por categoria | modal `<dialog>`, já no HTML |

O conteúdo dos modais **vem no HTML desde a entrega** — nada é buscado por
`fetch` no clique. É isso que mantém procedimentos e Dia da Noiva indexáveis
pelo Google, apesar de não terem endereço próprio.

## Como abrir

Sirva a pasta por HTTP — é o que reproduz a hospedagem real:

```bash
python -m http.server 8000
```

Abrir o `index.html` com dois cliques também funciona, mas o `file://`
costuma bloquear as fontes locais.

## Como editar o conteúdo

**Tudo o que o site diz sai do `dados.json`.** Endereço, horários, WhatsApp,
procedimentos, cronograma das noivas, equipe, avaliações, perguntas do FAQ e
os textos de cada seção. Depois de editar:

```bash
python gerar.py
```

O gerador reescreve o `index.html`, a `404.html`, o `sitemap.xml`, o
`robots.txt`, os favicons, a imagem de compartilhamento e os dois arquivos que
o GitHub Pages exige. Ele também calcula uma impressão digital do CSS e do JS
e a anexa como `?v=` nos ativos — assim uma atualização não fica escondida
atrás do cache de quem já visitou.

Nada que esteja em `_pendencias`, no fim do `dados.json`, aparece na
interface. É a lista do que ainda falta confirmar com a clínica.

## As fotografias

Onze dos quinze espaços estão preenchidos. As imagens vieram do site da
própria casa — `juhelenas.com.br` —, em 1440×2160 e 1300×1950, reduzidas para
1800px no lado maior e convertidas em WebP: **3,4 MB viraram 1,3 MB**, sem
perda visível.

Faltam quatro, e cada um por um motivo:

| espaço | por quê |
|---|---|
| `equipe-maria-gabriella` | não há como dizer qual rosto é o dela |
| `equipe-lill-leite` | idem |
| `equipe-leticia-oliveira` | idem |
| `trat-corpo-e-bem-estar` | não há foto de massagem ou terapia corporal |

Campo sem arquivo continua **em branco** — superfície um tom fora do fundo,
com filete, `aria-hidden`. Lê-se como espaço negativo intencional, não como
imagem quebrada, e é por isso que os quatro que faltam não estragam a página.

### Para preencher um espaço

1. salve o arquivo em `assets/img/fotos/<id>.webp` (ou `.avif`, `.jpg`, `.png`);
2. descreva a foto na seção `fotos` do `dados.json`;
3. rode `python gerar.py`.

O gerador troca o campo pela `<img>` sozinho, com `loading`, `decoding` e o
texto alternativo já escritos. **Não é preciso editar HTML** — e como ele
prefere `.webp` a `.jpg`, trocar o formato também não pede edição nenhuma.

A lista dos quinze identificadores, com o texto alternativo e a contagem do
que já foi preenchido, está em `_fonte/fotos-pendentes.txt`, reescrita a cada
geração. Mínimo recomendado: **1400px** no lado maior para retrato e painel,
**2400px** de largura para as bandas de abertura dos modais (2,45:1).

### A seção `fotos` do `dados.json`

```json
"casa-2": {
  "alt": "Atendimento no salão da Clínica Helenas: a cliente na cadeira...",
  "foco": "50% 35%"
}
```

`alt` é o texto alternativo real da imagem — substitui o genérico da seção e é
o que o leitor de tela anuncia. `foco` é o `object-position` do recorte, e
existe porque o mesmo arquivo é cortado em proporções muito diferentes: um
retrato 2:3 vira quase quadrado no painel da seção A Clínica e uma faixa
2,45:1 na banda de abertura do modal. No centro, o corte decepa cabeça.

### Direito de imagem

As fotos exibem clientes e modelos identificáveis. Já estão em uso comercial
no site da própria casa, mas **confirme com a clínica que a autorização de uso
de imagem cobre este site também** antes de publicar.

### Um ponto em aberto

A `.hero__placa` é `display:none` abaixo de 62rem, e o navegador baixa a foto
mesmo assim — medido, e também com `loading="lazy"`, que não evita o download
de um `<img>` sem caixa. São ~85 KB que todo celular paga por uma imagem que
não vê. A saída é decidir se a placa deve aparecer no celular.

## Como publicar

Rode `python gerar.py`, faça commit e suba. Em GitHub Pages, a partir da raiz
do branch. O `.nojekyll` existe para que a pasta `_fonte` não seja engolida
pelo Jekyll, que ignora tudo o que começa com sublinhado.

### Quando a clínica tiver domínio próprio

1. troque `site_url` no `dados.json` pelo domínio real e apague a linha
   `_site_url_pendente`;
2. rode `python gerar.py` — a URL canônica, o `og:url`, o sitemap e os links
   absolutos da `404.html` saem daí (hoje carregam o prefixo `/helenas/`);
3. aponte o DNS e cadastre o domínio em *Settings → Pages → Custom domain*;
4. fora do GitHub Pages, aponte a página de erro do servidor para `/404.html`;
5. cadastre o domínio no Google Search Console e envie `/sitemap.xml`.

## Os arquivos

```
dados.json              todo o conteúdo do site
gerar.py                lê o dados.json e escreve tudo o que é servido
index.html              gerado — não edite à mão
404.html                gerado — endereços que não existem, de qualquer profundidade
assets/css/helenas.css  escrito à mão
assets/js/app.js        escrito à mão
assets/js/vendor/       GSAP, ScrollTrigger e Lenis
assets/fonts/           Cormorant e Jost, subconjunto latino, woff2 variável
assets/img/fotos/       as fotografias, nomeadas pelo id do campo
_fonte/                 anotações de produção; nada aqui é servido como página
_diag.html              ferramenta de conferência: mede a página e lista erros
_pos.html               ferramenta de conferência: posição e altura de cada seção
_ver.html               ferramenta de conferência: abre a página numa altura fixa
```

Os três `_*.html` são ferramentas de desenvolvimento, não páginas do site.
Abra-os pelo servidor local. Eles não estão no `sitemap.xml` e a `robots.txt`
não os divulga; se incomodarem em produção, apague-os — nada depende deles.

## A regra que governa o CSS e o JS

**O layout sem a classe `.fx` é o layout legível, em fluxo normal.** Só o ramo
desktop-com-movimento do `gsap.matchMedia` liga o empilhamento das seções
pinadas. A consequência: celular, `prefers-reduced-motion`, JavaScript
quebrado e robô de busca veem a mesma página inteira e navegável.

Um script embutido no `<head>` esconde-para-animar antes da primeira pintura,
para não haver piscada — e desfaz isso sozinho se o `app.js` não confirmar que
subiu em 4 segundos. Nenhum conteúdo depende de JavaScript para ser visto.

## Acessibilidade

- navegação por teclado em tudo, com foco visível e ordem previsível;
- modais em `<dialog>` nativo: `Esc`, foco preso e inércia de fundo de graça;
- o menu do celular tranca a rolagem sem perder a posição da página;
- campos de fotografia vazios são `aria-hidden`: o leitor de tela não anuncia
  uma foto que não existe;
- contraste conferido; os numerais dourados usam um tom escurecido até 4,6:1.
