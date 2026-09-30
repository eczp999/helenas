/* ==========================================================================
   Clínica Helenas — V2. Comportamento da página única.

   Ordem de carregamento no HTML (esta ordem importa):
     lenis.css no <head>
     gsap.min.js → ScrollTrigger.min.js → lenis.min.js → este arquivo (defer)

   Regra que governa o arquivo: o layout SEM a classe .fx é o layout legível,
   em fluxo normal. Só o ramo desktop-com-movimento do gsap.matchMedia liga o
   empilhamento, e a limpeza sai na função RETORNADA pelo handler — nunca em
   ctx.add(), que executa na hora em vez de na saída.

    1. Guardas e entrada      5. Movimento (matchMedia)
    2. Lenis e a ponte        6. Cabeçalho, gaveta, trilho e tema
    3. Âncoras                7. Formulário e mapa
    4. Modais                 8. Recálculo
   ========================================================================== */
(() => {
  "use strict";

  const root = document.documentElement;
  const reduz = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* --------------------------------------------------------- 1. GUARDAS */
  // Sem as bibliotecas a página continua inteira e navegável: o CSS base já
  // é o layout em fluxo. Só o movimento não acontece.
  const temGsap = window.gsap && window.ScrollTrigger && window.Lenis;
  if (temGsap) gsap.registerPlugin(ScrollTrigger);
  // O script embutido no <head> desfaz o esconde-para-animar se isto não
  // chegar em 4 segundos. Sem esta linha, uma falha de rede deixaria a
  // página em branco.
  window.__helenasOk = true;

  // O navegador restauraria o scroll antes de as fontes, os pin-spacers e o
  // Lenis existirem — ou seja, com a página na altura errada.
  history.scrollRestoration = "manual";
  const hashInicial = location.hash;
  if (hashInicial) history.replaceState(null, "", location.pathname + location.search);
  window.scrollTo(0, 0);

  let lenis = null;

  if (temGsap) {
    // A barra de endereço do celular muda innerHeight e dispara resize a cada rolada.
    ScrollTrigger.config({ ignoreMobileResize: true });

    /* ------------------------------------------- 2. LENIS E A PONTE */
    lenis = new Lenis({
      lerp: 0.09,
      wheelMultiplier: 1,
      syncTouch: false,
      autoResize: true,
      anchors: false,            // as âncoras são feitas à mão (seção 3)
      respectReducedMotion: true,
      prevent: (n) => n.hasAttribute && n.hasAttribute("data-lenis-prevent"),
    });
    // Exposto para depuração e para ferramentas de captura de tela.
    window.lenis = lenis;

    // (a) ScrollTrigger lê a posição no mesmo frame em que o Lenis a escreveu.
    lenis.on("scroll", ScrollTrigger.update);
    // (b) Um único dono do loop. O ticker entrega segundos; lenis.raf quer ms.
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    // (c) Obrigatório: sem isto, um engasgo acima de 500ms faz o GSAP falsificar
    //     o delta, o Lenis integra um relógio irreal e o scroll teleporta.
    gsap.ticker.lagSmoothing(0);
  }

  /* --------------------------------------------------------- 3. ÂNCORAS */
  const cabecalho = document.querySelector("[data-topo]");
  const alturaTopo = () => (cabecalho ? cabecalho.offsetHeight : 0);

  function irPara(alvo, imediato = false) {
    const el = typeof alvo === "string" ? document.querySelector(alvo) : alvo;
    if (!el) return;
    if (!lenis) {
      el.scrollIntoView({ behavior: imediato || reduz() ? "auto" : "smooth" });
      return;
    }
    // Se o alvo está pinado, offsetTop aponta para o .pin-spacer. Role para o
    // número que o próprio trigger conhece.
    const st = ScrollTrigger.getAll().find((t) => t.pin && t.trigger === el);
    lenis.scrollTo(st ? st.start : el, {
      offset: st ? 0 : -alturaTopo(),
      immediate: imediato || reduz(),
      duration: 1.1,
    });
  }

  document.addEventListener("click", (ev) => {
    const a = ev.target.closest('a[href^="#"]:not([href="#"])');
    if (!a) return;
    const id = a.getAttribute("href");
    if (!document.querySelector(id)) return;
    ev.preventDefault();
    irPara(id);
    history.pushState(null, "", id);
  });

  /* ---------------------------------------------------------- 4. MODAIS */
  // O conteúdo dos modais já está no HTML desde a entrega — nada é buscado no
  // clique. É o que mantém procedimentos e Dia da Noiva indexáveis.
  let gatilho = null;
  let modalAberto = null;
  const flutuante = document.querySelector("[data-zap]");

  function abrirModal(modal, comHash = true) {
    if (!modal || modalAberto) return;
    fecharMenu(false);   // o botão Agendar da gaveta abre modal por cima dela
    gatilho = document.activeElement;
    modalAberto = modal;
    modal.removeAttribute("data-fechando");
    modal.showModal();                 // top-layer, ESC e inércia de fundo de graça
    if (lenis) lenis.stop();           // showModal não impede o Lenis de ler a roda
    if (flutuante) flutuante.dataset.visivel = "nao";
    if (comHash && modal.id) history.pushState({ modal: modal.id }, "", "#" + modal.id);
    const fechar = modal.querySelector("[data-fechar]");
    if (fechar) fechar.focus({ preventScroll: true });
  }

  function fecharModal(voltarHistorico = true) {
    const modal = modalAberto;
    if (!modal) return;
    modalAberto = null;
    modal.dataset.fechando = "sim";
    const encerrar = () => {
      modal.close();
      modal.removeAttribute("data-fechando");
      if (lenis) lenis.start();
      // preventScroll é essencial: sem ele o navegador rola a página ao
      // devolver o foco, e numa página de quinze telas isso é desastre.
      if (gatilho && gatilho.isConnected) gatilho.focus({ preventScroll: true });
      gatilho = null;
    };
    if (reduz()) encerrar();
    else setTimeout(encerrar, 230);
    if (voltarHistorico && location.hash === "#" + modal.id) history.back();
  }

  document.addEventListener("click", (ev) => {
    const abre = ev.target.closest("[data-abre]");
    if (abre) {
      ev.preventDefault();
      abrirModal(document.getElementById(abre.dataset.abre));
      return;
    }
    if (ev.target.closest("[data-fechar]")) {
      ev.preventDefault();
      fecharModal();
    }
  });

  // Clique fora da caixa fecha. O <dialog> ocupa a tela inteira, então o
  // alvo ser o próprio dialog significa que o clique caiu no backdrop.
  document.querySelectorAll("dialog.modal").forEach((m) => {
    m.addEventListener("click", (ev) => { if (ev.target === m) fecharModal(); });
    // ESC é nativo do <dialog>; interceptamos só para animar a saída.
    m.addEventListener("cancel", (ev) => { ev.preventDefault(); fecharModal(); });
  });

  // Voltar no navegador (e o gesto de voltar no celular) fecha o modal.
  window.addEventListener("popstate", () => {
    if (modalAberto) { fecharModal(false); return; }
    const alvo = location.hash && document.querySelector(location.hash);
    if (alvo && alvo.tagName === "DIALOG") abrirModal(alvo, false);
  });

  /* ------------------------------------------------------- 5. MOVIMENTO */
  if (temGsap) {
    // Retrato dos estilos inline ANTES de qualquer contexto, para o revert
    // não deixar transform/opacity pendurados ao trocar de breakpoint.
    ScrollTrigger.saveStyles("[data-fx], [data-pin], [data-painel], .linha > span, [data-parallax]");

    // Três pesos de entrada. O desfoque é exclusivo dos títulos: se tudo
    // entrasse desfocado ele viraria ruído e deixaria de significar foco.
    const alvoDe = (el) => {
      const tipo = el.dataset.fx;
      if (tipo === "etiqueta") return { autoAlpha: 1, y: 0, duration: 0.7, ease: "power2.out" };
      if (tipo === "titulo")   return { autoAlpha: 1, y: 0, filter: "blur(0px)", duration: 1, ease: "power3.out" };
      return { autoAlpha: 1, y: 0, duration: 0.9, ease: "power3.out" };
    };
    const inicioDe = (el) => {
      const tipo = el.dataset.fx;
      if (tipo === "etiqueta") return { autoAlpha: 0, y: 30 };
      if (tipo === "titulo")   return { autoAlpha: 0, y: 10, filter: "blur(3px)" };
      return { autoAlpha: 0, y: 24 };
    };
    // O hero é o LCP: entra só com opacidade e um deslocamento curto, sem
    // cascata longa, para não atrasar a percepção de carregamento.
    const revelarHero = () => {
      gsap.utils.toArray(".hero [data-fx]").forEach((el, i) => {
        gsap.fromTo(el, inicioDe(el), { ...alvoDe(el), duration: 0.8, delay: 0.42 + i * 0.07 });
      });
    };

    const mm = gsap.matchMedia();

    /* -------- 5a. Desktop com movimento -------- */
    mm.add("(min-width: 64rem) and (min-height: 41rem) and (prefers-reduced-motion: no-preference)", () => {
      root.classList.add("fx");

      // Hero: as linhas sobem de dentro do invólucro que corta. Dois
      // transforms, zero repaint.
      const linhas = gsap.utils.toArray(".hero .linha > span");
      if (linhas.length) {
        // O CSS esconde com translateY(101%). O GSAP lê esse transform e o
        // decompõe numa MATRIZ, onde não existe porcentagem: o 101% vira
        // y = 101.757px. Declarar só os extremos de yPercent anima a
        // porcentagem de 101 a 0 e deixa o pixel de pé — o <h1> termina uma
        // linha inteira abaixo do invólucro que corta e NUNCA aparece.
        // Por isso o y: 0 explícito nos dois extremos: é ele que apaga o
        // resíduo em pixels. Sem esta linha o título principal do site não
        // desenha em resolução nenhuma.
        gsap.fromTo(linhas, { yPercent: 101, y: 0 },
          { yPercent: 0, y: 0, duration: 1.15, ease: "expo.out", stagger: 0.08, delay: 0.12 });
      }
      revelarHero();

      // Hero sai com leve deslocamento: dá profundidade sem parallax caro.
      const hero = document.querySelector(".hero");
      if (hero) {
        gsap.to(".hero__grade", {
          yPercent: -9, autoAlpha: 0.35, ease: "none",
          scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: true },
        });
      }

      // Entradas padrão: uma por elemento, once, nunca raspadas pelo scroll.
      gsap.utils.toArray("[data-fx]:not(.hero [data-fx])").forEach((el) => {
        gsap.to(el, {
          ...alvoDe(el),
          scrollTrigger: { trigger: el, start: "top 88%", once: true },
        });
      });

      // PIN 1 — a casa. Os três painéis empilham e trocam com o scroll.
      document.querySelectorAll('[data-pin="pilha"]').forEach((secao) => {
        const palco = secao.querySelector("[data-palco]");
        const paineis = secao.querySelectorAll("[data-painel]");
        if (!palco || paineis.length < 2) return;

        gsap.set(paineis, { autoAlpha: 0 });
        gsap.set(paineis[0], { autoAlpha: 1 });

        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: {
            trigger: secao,
            start: "top top",
            // 0,9 de tela por painel extra: abaixo de 0,6 troca antes de dar
            // tempo de ler; acima de 1,2 o usuário acha que o scroll quebrou.
            end: () => "+=" + Math.round(window.innerHeight * 1.15 * (paineis.length - 1)),
            pin: true,
            pinSpacing: true,
            anticipatePin: 1,
            scrub: true,
            fastScrollEnd: true,
            invalidateOnRefresh: true,
            refreshPriority: 1,
          },
        });
        // Cada passo vale 1: a troca ocupa 0,4 e os 0,6 restantes são pausa.
        // A pausa é o que separa "sequência cinematográfica" de "enjoo".
        paineis.forEach((p, i) => {
          if (i === 0) return;
          const campoAnterior = paineis[i - 1].querySelector(".campo");
          const campoAtual = p.querySelector(".campo");
          tl.to(paineis[i - 1], { autoAlpha: 0, yPercent: -5, duration: 0.26 }, i - 1)
            .fromTo(p, { autoAlpha: 0, yPercent: 7 }, { autoAlpha: 1, yPercent: 0, duration: 0.3 }, i - 1 + 0.12)
            .to({}, { duration: 0.62 }, i - 1 + 0.38);   // a pausa: é ela que separa cinema de enjoo
          if (campoAnterior) tl.to(campoAnterior, { scale: 1.04, duration: 0.26 }, i - 1);
          if (campoAtual) tl.fromTo(campoAtual, { scale: 0.96 }, { scale: 1, duration: 0.42 }, i - 1 + 0.12);
        });
      });

      // A coluna das noivas fica fixa por CSS (position: sticky), não por pin.
      // Um set piece por página: dois pins medianos valem menos que um bom.

      // Parallax discreto nos campos: só transform, dentro de wrapper que corta.
      gsap.utils.toArray("[data-parallax]").forEach((el) => {
        const q = parseFloat(el.dataset.parallax) || 10;
        gsap.fromTo(el, { yPercent: -q / 2 }, {
          yPercent: q / 2, ease: "none",
          scrollTrigger: { trigger: el.parentElement, start: "top bottom", end: "bottom top", scrub: true },
        });
      });

      // A limpeza do que NÃO é GSAP vai aqui. Tweens, timelines, triggers e
      // pin-spacers criados acima são revertidos sozinhos.
      return () => root.classList.remove("fx");
    });

    /* -------- 5b. Celular e tablet: sem pin, sem parallax -------- */
    mm.add("(prefers-reduced-motion: no-preference)", () => {
      if (matchMedia("(min-width: 64rem) and (min-height: 41rem)").matches) return;
      // Mesma armadilha do ramo 5a: um gsap.set({yPercent: 0}) sozinho zera a
      // porcentagem e deixa o y em pixels que o GSAP extraiu do CSS — o
      // título do topo ficava invisível em TODO celular e tablet. O y: 0
      // explícito é o que resolve. Aqui a linha ainda sobe, só que mais
      // curta que no desktop: é a mesma ideia, em menos tela.
      const linhasCurtas = gsap.utils.toArray(".hero .linha > span");
      if (linhasCurtas.length) {
        gsap.fromTo(linhasCurtas, { yPercent: 101, y: 0 },
          { yPercent: 0, y: 0, duration: 0.85, ease: "expo.out", stagger: 0.06, delay: 0.1 });
      }
      gsap.utils.toArray("[data-fx]").forEach((el) => {
        gsap.fromTo(el, { autoAlpha: 0, y: 18 }, {
          autoAlpha: 1, y: 0, duration: 0.6, ease: "power2.out",
          scrollTrigger: { trigger: el, start: "top 92%", once: true },
        });
      });
    });

    /* -------- 5c. Movimento reduzido: tudo visível, só cross-fade -------- */
    mm.add("(prefers-reduced-motion: reduce)", () => {
      gsap.set("[data-fx], [data-painel], .linha > span", { clearProps: "all" });
      gsap.utils.toArray("[data-fx]").forEach((el) => {
        gsap.fromTo(el, { autoAlpha: 0 }, {
          autoAlpha: 1, duration: 0.35, ease: "none",
          scrollTrigger: { trigger: el, start: "top 95%", once: true },
        });
      });
    });
  }

  /* ------------------------------------- 6. CABEÇALHO, GAVETA E TRILHO */

  /* A gaveta é a ÚNICA navegação abaixo de 62rem: o .topo__nav está oculto
     nessa faixa. Sem este bloco o botão Menu não faz nada e o celular fica
     sem índice — só com o rolar. */
  const botaoMenu = document.querySelector("[data-menu-botao]");
  const gaveta = document.querySelector("[data-gaveta]");
  // A gaveta não é um <dialog>: sem isto o leitor de tela continuaria lendo a
  // página inteira por trás dela. O <dialog> dos modais ganha o mesmo de graça.
  const fundo = document.querySelectorAll("main, footer, [data-zap], [data-trilho]");
  const temInert = "inert" in HTMLElement.prototype;
  let menuAberto = false;

  function fecharMenu(devolverFoco = true) {
    if (!menuAberto) return;
    menuAberto = false;
    gaveta.dataset.aberta = "nao";
    botaoMenu.setAttribute("aria-expanded", "false");
    root.classList.remove("menu-aberto");
    if (temInert) fundo.forEach((el) => { el.inert = false; });
    if (lenis) lenis.start();
    if (devolverFoco) botaoMenu.focus({ preventScroll: true });
  }

  function abrirMenu() {
    if (menuAberto) return;
    menuAberto = true;
    gaveta.dataset.aberta = "sim";
    botaoMenu.setAttribute("aria-expanded", "true");
    // A trava é no CSS (overflow: hidden na raiz): preserva o scrollY, ao
    // contrário do truque de position: fixed no body. E o lenis.stop() cobre
    // a roda do mouse no tablet, que a trava de overflow sozinha não segura.
    root.classList.add("menu-aberto");
    if (temInert) fundo.forEach((el) => { el.inert = true; });
    if (lenis) lenis.stop();
  }

  if (botaoMenu && gaveta) {
    botaoMenu.addEventListener("click", () => (menuAberto ? fecharMenu() : abrirMenu()));

    // Clique num link: a gaveta fecha ANTES de o handler de âncoras da seção 3
    // rolar a página — o ouvinte daqui está mais perto do alvo que o de
    // document, então dispara primeiro e o Lenis já volta destravado.
    gaveta.addEventListener("click", (ev) => {
      if (ev.target.closest('a[href^="#"]')) fecharMenu(false);
    });

    document.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape" && menuAberto && !modalAberto) fecharMenu();
    });

    // Passou para a faixa de desktop com a gaveta aberta: o CSS a esconde com
    // display: none e a trava de rolagem ficaria presa sem dono.
    const faixaLarga = matchMedia("(min-width: 62rem)");
    const aoTrocar = () => { if (faixaLarga.matches) fecharMenu(false); };
    if (faixaLarga.addEventListener) faixaLarga.addEventListener("change", aoTrocar);
    else faixaLarga.addListener(aoTrocar);
  }

  const trilho = document.querySelector("[data-trilho]");
  const preenche = document.querySelector("[data-trilho-preenche]");

  if (flutuante || trilho) {
    let pendente = false;
    const uma = () => window.innerHeight || 800;

    const marcar = () => {
      const y = window.scrollY;
      const total = Math.max(1, document.documentElement.scrollHeight - uma());
      const p = Math.min(1, Math.max(0, y / total));

      if (flutuante && !modalAberto) flutuante.dataset.visivel = y > uma() * 1.1 ? "sim" : "nao";
      if (trilho) trilho.dataset.visivel = y > uma() * 0.9 && p < 0.97 ? "sim" : "nao";
      if (preenche) preenche.style.transform = "scaleY(" + p.toFixed(4) + ")";
    };

    addEventListener("scroll", () => {
      if (pendente) return;
      pendente = true;
      requestAnimationFrame(() => { marcar(); pendente = false; });
    }, { passive: true });
    addEventListener("load", marcar);
    marcar();
  }

  // Scrollspy e temperatura da seção, num trigger por seção — sem listener próprio.
  const secoes = document.querySelectorAll("main section[id]");
  if (temGsap && secoes.length) {
    secoes.forEach((sec) => {
      const link = document.querySelector('.topo__link[href="#' + sec.id + '"]');
      ScrollTrigger.create({
        trigger: sec,
        start: "top 45%",
        end: "bottom 45%",
        onToggle: (self) => {
          if (link) link.classList.toggle("is-ativo", self.isActive);
          if (!self.isActive) return;
          // O cabeçalho e o trilho são fixos: precisam saber sobre que
          // temperatura estão flutuando.
          if (sec.dataset.tema === "escuro") root.dataset.tema = "escuro";
          else root.removeAttribute("data-tema");
          // replaceState, nunca pushState: senão o botão Voltar vira dez cliques.
          if (!modalAberto) history.replaceState(null, "", "#" + sec.id);
        },
      });
    });
  }

  /* --------------------------------------------- 7. FORMULÁRIO E MAPA */
  const form = document.querySelector("[data-form]");
  if (form) {
    const aviso = form.querySelector("[data-aviso]");

    const erroDe = (campo) => {
      const e = campo.querySelector("input, textarea, select");
      if (!e) return "";
      if (e.validity.valueMissing) return e.dataset.faltando || "Preencha este campo.";
      if (e.validity.tooShort) return "Escreva um pouco mais.";
      return "";
    };
    const validar = (campo) => {
      const msg = erroDe(campo);
      const caixa = campo.querySelector("[data-erro]");
      const e = campo.querySelector("input, textarea, select");
      campo.dataset.invalido = msg ? "sim" : "nao";
      if (caixa) caixa.textContent = msg;
      if (e) e.setAttribute("aria-invalid", msg ? "true" : "false");
      return !msg;
    };

    form.querySelectorAll(".campo-form").forEach((campo) => {
      const e = campo.querySelector("input, textarea, select");
      if (!e) return;
      e.addEventListener("blur", () => validar(campo));
      e.addEventListener("input", () => { if (campo.dataset.invalido === "sim") validar(campo); });
    });

    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const campos = Array.from(form.querySelectorAll(".campo-form"));
      if (!campos.map(validar).every(Boolean)) {
        if (aviso) { aviso.hidden = false; aviso.textContent = "Confira os campos destacados antes de enviar."; }
        const primeiro = form.querySelector('[data-invalido="sim"] input, [data-invalido="sim"] textarea');
        if (primeiro) primeiro.focus();
        return;
      }
      const d = new FormData(form);
      const linhas = [
        "Olá! Vim pelo site da Clínica Helenas.", "",
        "Nome: " + (d.get("nome") || "").trim(),
        "Telefone: " + (d.get("telefone") || "").trim(),
      ];
      const assunto = (d.get("assunto") || "").trim();
      if (assunto) linhas.push("Assunto: " + assunto);
      const recado = (d.get("mensagem") || "").trim();
      if (recado) linhas.push("", recado);
      if (aviso) {
        aviso.hidden = false;
        aviso.textContent = "Abrindo o WhatsApp com a sua mensagem pronta. Se não abrir, use o botão ao lado.";
      }
      window.open(form.dataset.form + "?text=" + encodeURIComponent(linhas.join("\n")), "_blank", "noopener");
    });
  }

  const mapa = document.querySelector("[data-mapa]");
  if (mapa) {
    const carregar = () => {
      if (mapa.dataset.carregado === "sim") return;
      mapa.dataset.carregado = "sim";
      const f = document.createElement("iframe");
      f.src = mapa.dataset.mapa;
      f.title = mapa.dataset.titulo || "Mapa";
      f.loading = "lazy";
      f.referrerPolicy = "no-referrer-when-downgrade";
      f.setAttribute("allowfullscreen", "");
      // Antes da tarja, para o botão continuar por cima do iframe.
      mapa.insertBefore(f, mapa.firstChild);
    };

    // O lenis.css desliga o ponteiro de TODO iframe enquanto o scroll suave
    // está ligado — senão a roda do mouse daria zoom no Google em vez de rolar
    // a página. A tarja devolve o mapa a quem clicar nela de propósito. Nasce
    // aqui, e não no HTML, porque sem Lenis não há nada para destravar — um
    // botão morto seria pior que o mapa como está.
    if (lenis) {
      mapa.dataset.ativo = "nao";
      const tarja = document.createElement("button");
      tarja.type = "button";
      tarja.className = "mapa__destravar";
      tarja.textContent = "Ativar o mapa";
      tarja.addEventListener("click", () => {
        carregar();
        mapa.dataset.ativo = "sim";
      });
      mapa.appendChild(tarja);
    }
    if (!("IntersectionObserver" in window)) carregar();
    else {
      const olho = new IntersectionObserver((e) => {
        if (!e[0].isIntersecting) return;
        carregar();
        olho.disconnect();
      }, { rootMargin: "320px" });
      olho.observe(mapa);
    }
  }

  /* ------------------------------------------------------ 8. RECÁLCULO */
  if (temGsap) {
    let naFila = false;
    const recalcular = () => {
      if (naFila) return;
      naFila = true;
      requestAnimationFrame(() => { naFila = false; ScrollTrigger.refresh(); });
    };

    // Cormorant e Jost têm métricas bem diferentes das fontes de reserva:
    // a troca reflui cada parágrafo e move tudo o que está abaixo.
    if (document.fonts) document.fonts.ready.then(recalcular);

    addEventListener("load", () => {
      ScrollTrigger.refresh();
      const alvo = hashInicial && document.querySelector(hashInicial);
      if (!alvo) return;
      history.replaceState(null, "", hashInicial);
      if (alvo.tagName === "DIALOG") abrirModal(alvo, false);
      else irPara(alvo, true);
    });

    // Só o redimensionamento horizontal. No celular o vertical é a barra de
    // endereço aparecendo e sumindo a cada rolada.
    let larguraAnterior = window.innerWidth;
    addEventListener("resize", () => {
      if (window.innerWidth === larguraAnterior) return;
      larguraAnterior = window.innerWidth;
      recalcular();
    }, { passive: true });
  }
})();
