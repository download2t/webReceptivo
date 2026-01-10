/**
 * ordem_servico_detail.js
 * JavaScript para a página de detalhes da ordem de serviço
 * Funcionalidades: Copiar roteiro e Tradução via Argos Translate
 */

// Cache de traduções para evitar chamadas repetidas ao servidor
const translationCache = {};

// Função auxiliar para pegar o CSRF Token (Padrão Django)
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function copiarRoteiro() {
  const roteiroElement = document.getElementById("roteiroText");
  if (!roteiroElement) return;

  const text = roteiroElement.textContent;
  const btn = document.getElementById("copyRoteiroBtn");

  // Usar a API moderna do Clipboard
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        // Feedback visual
        const originalHTML = btn.innerHTML;
        btn.classList.remove("btn-success");
        btn.classList.add("btn-secondary"); // Muda cor temporariamente
        btn.innerHTML = '<i class="bi bi-check-lg"></i> Copiado!';
        btn.disabled = true;

        // Resetar após 2 segundos
        setTimeout(() => {
          btn.classList.remove("btn-secondary");
          btn.classList.add("btn-success");
          btn.classList.remove("disabled");
          btn.disabled = false;
          btn.innerHTML = originalHTML;
        }, 2000);
      })
      .catch((err) => {
        console.error("Erro ao copiar:", err);
        alert(
          "Erro ao copiar para a área de transferência. Por favor, selecione o texto e copie manualmente."
        );
      });
  } else {
    // Fallback para navegadores antigos
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed"; // Evita scroll
    textArea.style.opacity = "0";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
      document.execCommand("copy");
      alert("Copiado para a área de transferência!");
    } catch (err) {
      console.error("Erro ao copiar (fallback):", err);
      alert("Erro ao copiar. Por favor, copie manualmente.");
    }

    document.body.removeChild(textArea);
  }
}

async function traduzirRoteiro() {
  const languageSelector = document.getElementById("languageSelector");
  const targetLang = languageSelector.value;
  const roteiroText = document.getElementById("roteiroText");
  const loadingDiv = document.getElementById("loadingTranslation");
  const translateBtn = document.getElementById("translateBtn");

  // Se for português, restaurar original
  if (targetLang === "pt") {
    if (typeof roteiroOriginal !== "undefined") {
      roteiroText.textContent = roteiroOriginal;
    }
    return;
  }

  // Verificar cache (evita requisição se já traduziu para esse idioma)
  const cacheKey = `${targetLang}_${roteiroOriginal.length}`; // Chave simples baseada no tamanho
  if (translationCache[cacheKey]) {
    roteiroText.textContent = translationCache[cacheKey];
    return;
  }

  // Mostrar loading
  if (loadingDiv) loadingDiv.style.display = "block";
  if (translateBtn) translateBtn.disabled = true;

  try {
    // Tentar obter CSRF token de várias fontes
    let csrfToken = getCookie("csrftoken");
    if (!csrfToken) {
      csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;
    }
    if (!csrfToken) {
      csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    }

    const response = await fetch("/servicos/ajax/translate/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({
        text:
          typeof roteiroOriginal !== "undefined"
            ? roteiroOriginal
            : roteiroText.textContent,
        target_lang: targetLang,
      }),
    });

    // Verificar se a resposta é JSON antes de parsear
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      // Se não for JSON, provavelmente é um erro 500 do Django (HTML de erro)
      const errorText = await response.text();
      console.error("Erro no Servidor (Não-JSON):", errorText);
      throw new Error(
        "O servidor retornou um erro interno (500). Verifique os logs do Django."
      );
    }

    const data = await response.json();

    if (response.ok && data.success) {
      const translatedText = data.translated_text;

      // Salvar no cache
      translationCache[cacheKey] = translatedText;

      // Atualizar display
      roteiroText.textContent = translatedText;
    } else {
      const errorMsg = data.error || "Erro desconhecido na tradução";
      console.error("Erro da API:", errorMsg);
      alert("Falha na tradução: " + errorMsg);
    }
  } catch (error) {
    console.error("Erro na requisição:", error);
    alert("Erro de comunicação: " + error.message);
    // Restaura texto original em caso de erro grave
    if (typeof roteiroOriginal !== "undefined") {
      roteiroText.textContent = roteiroOriginal;
      languageSelector.value = "pt";
    }
  } finally {
    if (loadingDiv) loadingDiv.style.display = "none";
    if (translateBtn) translateBtn.disabled = false;
  }
}

// Inicialização
document.addEventListener("DOMContentLoaded", function () {
  // Adicionar listener para traduzir automaticamente ao mudar o select
  const languageSelector = document.getElementById("languageSelector");
  if (languageSelector) {
    languageSelector.addEventListener("change", function () {
      // Pequeno delay para UX
      setTimeout(traduzirRoteiro, 100);
    });
  }
});
