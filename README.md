# Site da Clínica Helenas — Londrina/PR

**No ar em https://eczp999.github.io/helenas/**

Site institucional e comercial da Clínica Helenas: estética avançada e salão
de beleza no mesmo endereço, com o Dia da Noiva como especialidade da casa.

Doze páginas estáticas, sem Node, sem framework, sem build de JavaScript.
Todo o conteúdo sai de um arquivo só (`dados.json`) e um script Python
reescreve o HTML.

> O endereço acima é o de apresentação, servido pelo GitHub Pages. Ele fica
> num subcaminho (`/helenas/`), e é por isso que `site_url`, no `dados.json`,
> precisa ser trocado quando a clínica tiver domínio próprio — ver
> **Como publicar**.

---

## Como abrir

O site é estático. Para ver localmente, sirva a pasta por HTTP — é o que
reproduz uma hospedagem real, onde `/procedimentos/` resolve sozinho:

```bash
python -m http.server 8000
```

Abrir o `index.html` com dois cliques também funciona: há um trecho em
`assets/js/helenas.js` que, só no protocolo `file://`, completa os links de
pasta com `index.html`. Numa hospedagem esse trecho nunca roda.

## Como publicar

Hoje o site é servido pelo **GitHub Pages**, a partir da raiz do branch
`main`. Publicar uma alteração é `python gerar.py`, commit e push — o Pages
reconstrói sozinho em cerca de um minuto. O arquivo `.nojekyll` existe para
que os arquivos sejam servidos exatamente como estão.

### Quando a clínica tiver domínio próprio

1. troque `site_url` no `dados.json` pelo domínio real e apague a linha
   `_site_url_pendente`;
2. rode `python gerar.py` (as URLs canônicas, o sitemap e os links absolutos
   da 404 saem daí — hoje eles carregam o prefixo `/helenas/`);
3. aponte o DNS para o GitHub Pages e cadastre o domínio em
   *Settings → Pages → Custom domain*, ou mude para outra hospedagem
   estática: Netlify, Vercel, Cloudflare Pages, S3 ou hospedagem
   compartilhada servem a pasta do mesmo jeito;
4. fora do GitHub Pages, aponte a página de erro do servidor para `/404.html`;
5. cadastre o domínio no Google Search Console e envie `/sitemap.xml`.

Não é preciso subir `_fonte/`, `gerar.py` nem `dados.json` para o site
funcionar — mas eles ficam versionados porque são a fonte do conteúdo, e
nenhum deles é servido como página.

## Como editar o conteúdo

**Tudo o que o site diz sai do `dados.json`.** Endereço, horários, WhatsApp,
procedimentos, cronograma das noivas, equipe, avaliações, perguntas do FAQ e
os textos de cada seção. Depois de editar:

```bash
python gerar.py
```

O gerador reescreve as doze páginas, o `sitemap.xml`, o `robots.txt`, os
favicons e a imagem de compartilhamento. Ele também calcula uma impressão
digital do CSS e do JS e a anexa como `?v=` nos ativos — assim uma
atualização não fica escondida atrás do cache de quem já visitou.

Para conferir se nada quebrou:

```bash
python _fonte/verificar.py
```

O verificador reclama de link morto, âncora inexistente, `<title>` fora de
tamanho, hierarquia de cabeçalhos quebrada, imagem sem alternativa textual,
link de WhatsApp com número diferente do `dados.json`, marcador de pendência
que vazou para o texto visível, promessa de resultado e clichê de site de
estética. Sai com código 1 se achar qualquer coisa — dá para pendurar num
hook de commit.

## Como colocar as fotos

Esta é a única coisa que falta para o site ficar completo.

O layout inteiro já está montado com **29 espaços de fotografia**. Enquanto a
foto real não chega, cada espaço mostra uma superfície da marca com o
monograma — nunca banco de imagens, nunca imagem gerada.

Para preencher, salve o arquivo em `assets/img/fotos/` com o nome do espaço e
rode `python gerar.py`:

```
assets/img/fotos/hero.jpg
assets/img/fotos/equipe-julia-helenas.jpg
assets/img/fotos/espaco-recepcao.webp
```

O gerador acha sozinho e troca o espaço reservado pela imagem, com
`loading="lazy"` em todas menos a do topo da home. Não é preciso editar HTML.

A lista completa — nome do arquivo, onde a foto aparece e o texto alternativo
já escrito — está em **`_fonte/fotos-pendentes.txt`**, reescrito a cada
geração, com a contagem de quantas já foram preenchidas. As orientações de
tamanho e recorte estão em `assets/img/fotos/LEIA-ME.txt`.

Prioridade, se as fotos chegarem aos poucos:

1. `hero` — o topo da home;
2. `equipe-julia-helenas` — o retrato da fundadora;
3. `noiva-principal` e `noivas-abertura` — a especialidade da casa;
4. `espaco-*` — o mosaico do ambiente;
5. o resto.

---

## O que existe

| Página | Endereço | O que faz |
| --- | --- | --- |
| Home | `/` | Hero, números, manifesto, as cinco frentes, diferenciais, faixa de noivas, espaço, avaliações, FAQ curto, localização |
| A Clínica | `/a-clinica/` | Origem, método de trabalho, o espaço |
| Procedimentos | `/procedimentos/` | Índice das quatro categorias |
| Estética facial | `/procedimentos/estetica-facial/` | Limpeza, rejuvenescimento, toxina, preenchimento |
| Corpo e bem-estar | `/procedimentos/corpo-e-bem-estar/` | Massagens |
| Cabelo e Head Spa | `/procedimentos/cabelo-e-head-spa/` | Head Spa, escova, penteado |
| Beleza e detalhes | `/procedimentos/beleza-e-detalhes/` | Sobrancelha, maquiagem, unhas, depilação |
| Noivas | `/noivas/` | Cronograma do Dia da Noiva, o que inclui, acompanhantes |
| Equipe | `/equipe/` | Julia Helenas e a equipe |
| Contato | `/contato/` | Dados, horários, formulário, mapa |
| Privacidade | `/privacidade/` | O que o site faz com os dados |
| Erro | `/404.html` | Página de endereço não encontrado |

### Arquivos

```
dados.json                 todo o conteúdo do site
gerar.py                   lê o dados.json e escreve as páginas
_fonte/verificar.py        confere o HTML gerado
_fonte/fotos-pendentes.txt relatório das fotos (gerado)
assets/css/helenas.css     folha única, em 18 seções numeradas
assets/js/helenas.js       comportamento, sem dependências
assets/fonts/              Cormorant Garamond e Jost, variáveis, subconjunto latino
assets/img/fotos/          onde entram as fotos reais
```

---

## Decisões que valem explicação

**O formulário entrega no WhatsApp.** O site é estático e a clínica já atende
por WhatsApp. Em vez de um formulário que manda e-mail para uma caixa que
ninguém abre, o envio monta a mensagem com o que a pessoa escreveu e abre a
conversa com o texto pronto. Nada é armazenado no site — por isso a página de
privacidade pode dizer que não há cookie nem rastreador.

**Nenhum preço aparece.** O único valor público encontrado foi o Head Spa numa
campanha de terceiros. Publicar tabela de preços de estética é decisão
comercial da clínica, não do site.

**Não há seção de tecnologias.** Um site de clínica premium normalmente
apresenta os equipamentos. Não foi possível confirmar quais aparelhos a
Helenas usa, e inventar marca de equipamento seria pior do que a ausência.
Quando a clínica informar, a seção entra na página A Clínica — o
`_pendencias.aparelhos` no `dados.json` guarda o lembrete.

**Nenhuma promessa de resultado.** Resultado estético depende de pele,
histórico, idade e cuidado em casa. O texto explica o que cada procedimento
faz e o que ele não faz. O verificador trata promessa de resultado como erro.

**As fotos não foram substituídas por banco de imagens.** O briefing pedia
material real da clínica. Colocar foto de stock de uma mulher genérica
descaracterizaria a casa e passaria despercebido até o dia em que alguém
notasse — os espaços reservados deixam a pendência visível e fáceis de
preencher.

---

## Identidade

Tirada do próprio material da clínica: o monograma `ch` em círculo, o rosé do
perfil e dos destaques, o marfim quente do fundo.

| Papel | Token | Valor |
| --- | --- | --- |
| Fundo | `--porcelana` | `#faf6f2` |
| Seção alternada | `--areia` | `#f3eae2` |
| Seção escura | `--carvao` | `#211a17` |
| Texto | `--tinta` | `#2b211d` |
| Marca | `--rose` / `--rose-forte` | `#b8807c` / `#8f5a56` |
| Filete | `--ouro` | `#b08d57` |

Tipografia: **Cormorant Garamond** (títulos, romana e itálica) e **Jost**
(texto e interface). As duas são variáveis, auto-hospedadas, com subconjunto
latino — 108 KB somados, sem chamada a servidor externo. A página inteira,
com fontes, CSS e JS, fica em torno de 190 KB antes da compressão.

Os tokens todos estão no topo do `helenas.css`, seção 2. Mudar a marca inteira
é mudar aquelas linhas.

---

## Dados da clínica usados no site

Conferidos em fontes públicas em setembro de 2026. Quando algum mudar, o lugar
de corrigir é o `dados.json`.

- **Endereço:** Av. Presidente Castelo Branco, 180 — Presidente, Londrina/PR,
  CEP 86061-335
- **WhatsApp:** (43) 99199-4020
- **Horário:** terça a sábado, das 9h às 18h30
- **Instagram:** [@clinicahelenas](https://www.instagram.com/clinicahelenas/)
- **Google:** 4,8 em 64 avaliações
- **Razão social:** Clínica Helenas e Cia LTDA — CNPJ 47.258.431/0001-16,
  aberta em 22/07/2022
- **Fundadora:** Julia Helenas, biomédica esteta e maquiadora
  ([@ju.helenas](https://www.instagram.com/ju.helenas/))

## O que ainda falta confirmar

A lista completa está em `_pendencias`, no fim do `dados.json`. Nada que esteja
lá aparece no site. Os itens que mais mudam a página:

- **domínio** — trocar `site_url`;
- **fotografia** — os 29 espaços;
- **equipe** — confirmar grafia dos nomes, funções e formações de Maria
  Gabriella, Lill Leite e Letícia Oliveira, e escrever uma bio curta para cada
  uma (enquanto `bio` estiver vazia, o bloco de texto não é renderizado);
- **estacionamento, formas de pagamento e acessibilidade do local** — três
  perguntas que clientes fazem e que hoje o site não responde;
- **aparelhos e tecnologias** — abre uma seção nova em A Clínica;
- **responsável técnico** — para o rodapé, se houver.
