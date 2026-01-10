/**
 * ordem_servico_detail.js
 * JavaScript para a página de detalhes da ordem de serviço
 */

const translationCache = {};

// Função auxiliar para pegar CSRF Token
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

  // innerText é crucial para manter a quebra de linha visual correta
  const text = roteiroElement.innerText;
  const btn = document.getElementById("copyRoteiroBtn");

  // API Clipboard Moderna
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        const originalHTML = btn.innerHTML;
        btn.classList.remove("btn-success");
        btn.classList.add("btn-dark");
        btn.innerHTML = '<i class="bi bi-check-lg"></i> Copiado!';

        setTimeout(() => {
          btn.classList.remove("btn-dark");
          btn.classList.add("btn-success");
          btn.innerHTML = originalHTML;
        }, 2000);
      })
      .catch((err) => {
        console.error("Erro ao copiar:", err);
        fallbackCopia(text);
      });
  } else {
    fallbackCopia(text);
  }
}

function fallbackCopia(text) {
  const textArea = document.createElement("textarea");
  textArea.value = text;
  document.body.appendChild(textArea);
  textArea.select();
  try {
    document.execCommand("copy");
    alert("Copiado para a área de transferência!");
  } catch (err) {
    alert("Erro ao copiar. Selecione manualmente.");
  }
  document.body.removeChild(textArea);
}

async function traduzirRoteiro() {
  const languageSelector = document.getElementById("languageSelector");
  const targetLang = languageSelector.value;
  const roteiroText = document.getElementById("roteiroText");
  const loadingDiv = document.getElementById("loadingTranslation");
  const avisoErro = document.getElementById("avisoErro");
  const translateBtn = document.getElementById("translateBtn");

  // 1. Limpar aviso de erro
  if (avisoErro) avisoErro.style.display = "none";

  // 2. Se PT, restaura original imediatamente
  if (targetLang === "pt") {
    if (typeof roteiroOriginal !== "undefined") {
      roteiroText.textContent = roteiroOriginal;
    }
    return;
  }

  // 3. Verificar Cache
  const cacheKey = `${targetLang}_${roteiroOriginal.length}`;
  if (translationCache[cacheKey]) {
    roteiroText.textContent = translationCache[cacheKey];
    return;
  }

  // 4. Ativar Loading
  if (loadingDiv) loadingDiv.style.display = "block";
  if (translateBtn) translateBtn.disabled = true;
  if (languageSelector) languageSelector.disabled = true;

  try {
    // 5. Buscar Token CSRF
    let csrfToken = document.getElementById("csrf_token_safe")?.value;
    if (!csrfToken) {
      csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;
    }
    if (!csrfToken) {
      csrfToken = getCookie("csrftoken");
    }

    if (!csrfToken) throw new Error("Token de segurança não encontrado.");

    // 6. Requisição
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

    // 7. Validar Resposta JSON
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error("Erro servidor (500/403).");
    }

    const data = await response.json();

    if (response.ok && data.success) {
      const translatedText = data.translated_text;
      translationCache[cacheKey] = translatedText;
      roteiroText.textContent = translatedText;
    } else {
      throw new Error(data.error || "Erro desconhecido");
    }
  } catch (error) {
    console.error("Erro tradução:", error);

    // Exibir aviso vermelho discreto
    if (avisoErro) {
      avisoErro.style.display = "inline-block";
      // Se quiser o texto do erro: avisoErro.innerText = "Erro: " + error.message;
    }

    // Restaura para PT para não deixar texto quebrado
    if (typeof roteiroOriginal !== "undefined") {
      roteiroText.textContent = roteiroOriginal;
      languageSelector.value = "pt";
    }
  } finally {
    if (loadingDiv) loadingDiv.style.display = "none";
    if (translateBtn) translateBtn.disabled = false;
    if (languageSelector) languageSelector.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const languageSelector = document.getElementById("languageSelector");
  if (languageSelector) {
    languageSelector.addEventListener("change", () => traduzirRoteiro());
  }
});
