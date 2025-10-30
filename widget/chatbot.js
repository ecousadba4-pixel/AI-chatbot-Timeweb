(function () {
  const widgetRoot = document.querySelector('.twb-chatbot');
  if (!widgetRoot) return;

  const apiEndpoint = widgetRoot.dataset.apiEndpoint;
  if (!apiEndpoint) {
    console.error('Не указан адрес API для виджета чата. Добавьте data-api-endpoint на контейнер.');
    return;
  }

  const widgetBtn = document.createElement('button');
  widgetBtn.type = 'button';
  widgetBtn.className = 'twb-chatbot-button';
  widgetBtn.setAttribute('aria-label', 'Открыть чат с AI-консьержем');
  widgetBtn.setAttribute('aria-expanded', 'false');
  widgetBtn.innerHTML =
    '<span class="twb-chatbot-button-icon" aria-hidden="true">' +
    '<svg width="36" height="36" viewBox="0 0 36 36" focusable="false">' +
    '<defs>' +
    '<linearGradient id="twbBtnGradient" x1="0%" y1="0%" x2="100%" y2="100%">' +
    '<stop offset="0%" stop-color="#8a9d4c"></stop>' +
    '<stop offset="100%" stop-color="#6b7c3a"></stop>' +
    '</linearGradient>' +
    '</defs>' +
    '<circle cx="18" cy="18" r="17" fill="url(#twbBtnGradient)"></circle>' +
    '<text x="18" y="26" text-anchor="middle" font-family="Prata, serif" font-size="20" fill="#fff" font-weight="700">AI</text>' +
    '</svg>' +
    '</span>';

  const widgetBox = document.createElement('div');
  widgetBox.className = 'twb-chatbot-box';
  widgetBox.setAttribute('role', 'dialog');
  widgetBox.setAttribute('aria-label', 'Чат с AI-консьержем');
  widgetBox.setAttribute('aria-modal', 'false');
  widgetBox.innerHTML = `
    <div class="twb-chatbot-header">
      <div class="twb-chatbot-header-text">
        <span class="twb-chatbot-title">AI консьерж</span>
        <span class="twb-chatbot-subtitle">Отвечу на вопросы о нашем отеле</span>
      </div>
      <button type="button" class="twb-chatbot-close" aria-label="Закрыть чат">×</button>
    </div>
    <div id="twb-chatbot-history" class="twb-chatbot-history" aria-live="polite">
      <div class="twb-chatbot-placeholder">Задайте вопрос о нашем отеле</div>
    </div>
    <form id="twb-chatbot-form" class="twb-chatbot-form">
      <input
        id="twb-chatbot-input"
        class="twb-chatbot-input"
        type="text"
        placeholder="Спроси про услуги, номера, часы работы..."
        autocomplete="off"
        required
      />
      <button type="submit" class="twb-chatbot-send" aria-label="Отправить сообщение">➤</button>
    </form>
  `;

  document.body.appendChild(widgetBtn);
  document.body.appendChild(widgetBox);

  const history = widgetBox.querySelector('#twb-chatbot-history');
  const form = widgetBox.querySelector('#twb-chatbot-form');
  const input = widgetBox.querySelector('#twb-chatbot-input');
  const closeBtn = widgetBox.querySelector('.twb-chatbot-close');

  function escapeHTML(str) {
    return String(str).replace(/[&<>"']/g, (char) => {
      switch (char) {
        case '&':
          return '&amp;';
        case '<':
          return '&lt;';
        case '>':
          return '&gt;';
        case '"':
          return '&quot;';
        case "'":
          return '&#39;';
        default:
          return char;
      }
    });
  }

  function addMessage(text, role) {
    if (!history) return;

    if (history.firstElementChild && history.firstElementChild.classList.contains('twb-chatbot-placeholder')) {
      history.firstElementChild.remove();
    }

    const wrapper = document.createElement('div');
    wrapper.className = `twb-chatbot-message twb-chatbot-${role}`;
    wrapper.innerHTML = `<span>${escapeHTML(text)}</span>`;
    history.appendChild(wrapper);
    history.scrollTop = history.scrollHeight;
    return wrapper;
  }

  function showTyping() {
    return addMessage('AI консьерж готовит ответ...', 'typing');
  }

  function openChat() {
    widgetBox.classList.add('twb-chatbot-box-visible');
    widgetBtn.classList.add('twb-chatbot-button-hidden');
    widgetBtn.setAttribute('aria-expanded', 'true');
    setTimeout(() => {
      input?.focus();
    }, 150);
  }

  function closeChat() {
    widgetBox.classList.remove('twb-chatbot-box-visible');
    widgetBtn.classList.remove('twb-chatbot-button-hidden');
    widgetBtn.setAttribute('aria-expanded', 'false');
    widgetBtn.focus();
  }

  widgetBtn.addEventListener('click', openChat);
  widgetBtn.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      openChat();
    }
  });

  closeBtn?.addEventListener('click', closeChat);
  closeBtn?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      closeChat();
    }
  });

  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!input) return;

    const question = input.value.trim();
    if (!question) return;

    addMessage(question, 'user');
    input.value = '';

    const typingBubble = showTyping();

    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });

      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        data = null;
      }

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      const answer = data && typeof data.answer === 'string' && data.answer.trim()
        ? data.answer
        : 'Извините, ответ не получен.';

      if (typingBubble) {
        typingBubble.innerHTML = `<span>${escapeHTML(answer)}</span>`;
        typingBubble.className = 'twb-chatbot-message twb-chatbot-agent';
      } else {
        addMessage(answer, 'agent');
      }
    } catch (error) {
      if (typingBubble) {
        typingBubble.innerHTML =
          '<span>Ошибка соединения с сервером. Попробуйте позже.</span>';
        typingBubble.className = 'twb-chatbot-message twb-chatbot-error';
      } else {
        addMessage('Ошибка соединения с сервером. Попробуйте позже.', 'error');
      }
      console.error(error);
    }
  });
})();
