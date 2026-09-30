/* ==========================================================================
   Clínica Helenas — comportamento de interface
   Sem dependências. Tudo degrada: sem JS, o site continua navegável.

   1. Cabeçalho preso      4. Formulário
   2. Menu de bolso        5. Mapa sob demanda
   3. Revelação na rolagem 6. Abertura em file://
   ========================================================================== */
(function () {
  "use strict";

  var pouco = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* -----------------------------------------------------------------------
     1. Cabeçalho: ganha fundo assim que a página sai do topo
     ----------------------------------------------------------------------- */
  var topo = document.querySelector("[data-topo]");
  var zap = document.querySelector("[data-zap]");

  if (topo || zap) {
    var marcar = function () {
      var y = window.scrollY;
      if (topo) topo.dataset.preso = y > 12 ? "sim" : "nao";
      if (zap) zap.dataset.visivel = y > 520 ? "sim" : "nao";
    };
    var pendente = false;
    window.addEventListener("scroll", function () {
      if (pendente) return;
      pendente = true;
      window.requestAnimationFrame(function () {
        marcar();
        pendente = false;
      });
    }, { passive: true });
    // Chegar por âncora (/#local) posiciona a página sem disparar `scroll`.
    window.addEventListener("load", marcar);
    window.addEventListener("hashchange", marcar);
    marcar();
  }

  /* -----------------------------------------------------------------------
     2. Menu de bolso
     ----------------------------------------------------------------------- */
  var botaoMenu = document.querySelector("[data-menu-botao]");
  var gaveta = document.querySelector("[data-gaveta]");

  if (botaoMenu && gaveta) {
    var abrir = function (estado) {
      botaoMenu.setAttribute("aria-expanded", String(estado));
      gaveta.dataset.aberta = estado ? "sim" : "nao";
      document.body.style.overflow = estado ? "hidden" : "";
      if (estado) {
        var primeiro = gaveta.querySelector("a, button");
        if (primeiro) primeiro.focus();
      }
    };

    botaoMenu.addEventListener("click", function () {
      abrir(botaoMenu.getAttribute("aria-expanded") !== "true");
    });

    gaveta.addEventListener("click", function (ev) {
      if (ev.target.closest("a")) abrir(false);
    });

    document.addEventListener("keydown", function (ev) {
      if (ev.key !== "Escape") return;
      if (botaoMenu.getAttribute("aria-expanded") !== "true") return;
      abrir(false);
      botaoMenu.focus();
    });

    // Prender o foco dentro da gaveta enquanto ela estiver aberta.
    gaveta.addEventListener("keydown", function (ev) {
      if (ev.key !== "Tab") return;
      var focaveis = gaveta.querySelectorAll("a[href], button:not([disabled])");
      if (!focaveis.length) return;
      var primeiro = focaveis[0];
      var ultimoFoco = focaveis[focaveis.length - 1];
      if (ev.shiftKey && document.activeElement === primeiro) {
        ev.preventDefault();
        ultimoFoco.focus();
      } else if (!ev.shiftKey && document.activeElement === ultimoFoco) {
        ev.preventDefault();
        botaoMenu.focus();
      }
    });

    window.matchMedia("(min-width: 62rem)").addEventListener("change", function (ev) {
      if (ev.matches) abrir(false);
    });
  }

  /* -----------------------------------------------------------------------
     3. Revelação na rolagem
     ----------------------------------------------------------------------- */
  var reveláveis = document.querySelectorAll(".revelar");
  if (reveláveis.length) {
    if (pouco || !("IntersectionObserver" in window)) {
      reveláveis.forEach(function (el) { el.classList.add("visivel"); });
    } else {
      var olho = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (entrada) {
          if (!entrada.isIntersecting) return;
          entrada.target.classList.add("visivel");
          olho.unobserve(entrada.target);
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
      reveláveis.forEach(function (el) { olho.observe(el); });
    }
  }

  /* -----------------------------------------------------------------------
     4. Formulário: monta a mensagem e entrega no WhatsApp
        Site estático, sem servidor. O envio é uma conversa, não um e-mail
        que ninguém lê.
     ----------------------------------------------------------------------- */
  var form = document.querySelector("[data-form]");
  if (form) {
    var aviso = form.querySelector("[data-aviso]");

    var erroDoCampo = function (campo) {
      var entrada = campo.querySelector("input, textarea, select");
      if (!entrada) return "";
      if (entrada.validity.valueMissing) return entrada.dataset.faltando || "Preencha este campo.";
      if (entrada.validity.tooShort) return "Escreva um pouco mais.";
      if (entrada.validity.patternMismatch) return entrada.dataset.formato || "Confira o formato.";
      return "";
    };

    var validar = function (campo) {
      var mensagem = erroDoCampo(campo);
      var caixa = campo.querySelector("[data-erro]");
      campo.dataset.invalido = mensagem ? "sim" : "nao";
      if (caixa) caixa.textContent = mensagem;
      var entrada = campo.querySelector("input, textarea, select");
      if (entrada) entrada.setAttribute("aria-invalid", mensagem ? "true" : "false");
      return !mensagem;
    };

    form.querySelectorAll(".campo").forEach(function (campo) {
      var entrada = campo.querySelector("input, textarea, select");
      if (!entrada) return;
      entrada.addEventListener("blur", function () { validar(campo); });
      entrada.addEventListener("input", function () {
        if (campo.dataset.invalido === "sim") validar(campo);
      });
    });

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var campos = Array.prototype.slice.call(form.querySelectorAll(".campo"));
      var valido = campos.map(validar).every(Boolean);

      if (!valido) {
        if (aviso) {
          aviso.hidden = false;
          aviso.textContent = "Confira os campos destacados antes de enviar.";
        }
        var primeiroErro = form.querySelector('[data-invalido="sim"] input, [data-invalido="sim"] textarea');
        if (primeiroErro) primeiroErro.focus();
        return;
      }

      var dados = new FormData(form);
      var linhas = [
        "Olá! Vim pelo site da Clínica Helenas.",
        "",
        "Nome: " + (dados.get("nome") || "").trim(),
        "Telefone: " + (dados.get("telefone") || "").trim()
      ];
      var assunto = (dados.get("assunto") || "").trim();
      if (assunto) linhas.push("Assunto: " + assunto);
      var recado = (dados.get("mensagem") || "").trim();
      if (recado) linhas.push("", recado);

      var destino = form.dataset.form + "?text=" + encodeURIComponent(linhas.join("\n"));

      if (aviso) {
        aviso.hidden = false;
        aviso.textContent = "Abrindo o WhatsApp com a sua mensagem pronta. Se não abrir, fale com a gente pelo botão ao lado.";
      }
      window.open(destino, "_blank", "noopener");
    });
  }

  /* -----------------------------------------------------------------------
     5. Mapa: só carrega quando chega perto da tela
     ----------------------------------------------------------------------- */
  var mapa = document.querySelector("[data-mapa]");
  if (mapa) {
    var carregar = function () {
      if (mapa.dataset.carregado === "sim") return;
      mapa.dataset.carregado = "sim";
      var quadro = document.createElement("iframe");
      quadro.src = mapa.dataset.mapa;
      quadro.title = mapa.dataset.titulo || "Mapa";
      quadro.loading = "lazy";
      quadro.referrerPolicy = "no-referrer-when-downgrade";
      quadro.setAttribute("allowfullscreen", "");
      mapa.appendChild(quadro);
    };
    if (!("IntersectionObserver" in window)) {
      carregar();
    } else {
      var olhoMapa = new IntersectionObserver(function (entradas) {
        if (!entradas[0].isIntersecting) return;
        carregar();
        olhoMapa.disconnect();
      }, { rootMargin: "320px" });
      olhoMapa.observe(mapa);
    }
  }

  /* -----------------------------------------------------------------------
     6. Abertura por duplo clique (protocolo file://)
        Numa hospedagem real este trecho nunca roda: as pastas resolvem
        sozinhas o index.html.
     ----------------------------------------------------------------------- */
  if (window.location.protocol === "file:") {
    document.querySelectorAll('a[href$="/"]').forEach(function (a) {
      var href = a.getAttribute("href");
      if (href && href.indexOf("http") !== 0) a.setAttribute("href", href + "index.html");
    });
  }
})();
