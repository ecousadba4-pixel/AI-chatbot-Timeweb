(function () {
  const widgetRoot = document.querySelector('.twb-chatbot');
  if (!widgetRoot) return;

  const apiEndpoint = widgetRoot.dataset.apiEndpoint;
  if (!apiEndpoint) {
    console.error('Не указан адрес API для виджета чата. Добавьте data-api-endpoint на контейнер.');
    return;
  }

  const styleId = 'twb-chatbot-style';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      .twb-chatbot-button {
        position: fixed;
        right: 24px;
        bottom: 24px;
        width: 60px;
        height: 60px;
        border: none;
        border-radius: 50%;
        background: transparent;
        padding: 0;
        cursor: pointer;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.18);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        z-index: 2147483000;
      }

      .twb-chatbot-button:focus {
        outline: 2px solid #c9d99a;
        outline-offset: 3px;
      }

      .twb-chatbot-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.22);
      }

      .twb-chatbot-button-hidden {
        display: none !important;
      }

      .twb-chatbot-box {
        position: fixed;
        right: 24px;
        bottom: 96px;
        width: 360px;
        max-width: calc(100vw - 48px);
        height: 520px;
        max-height: 75vh;
        background: #fff;
        border-radius: 18px;
        box-shadow: 0 12px 40px rgba(138, 157, 76, 0.25);
        display: none;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid #e6ead9;
        z-index: 2147482999;
        color: #252a20;
        font-family: 'Open Sans', Arial, sans-serif;
      }

      .twb-chatbot-box-visible {
        display: flex;
      }

      .twb-chatbot-header {
        background: linear-gradient(135deg, #8a9d4c, #6b7c3a);
        padding: 18px 50px 18px 20px;
        border-radius: 18px 18px 0 0;
        display: flex;
        align-items: center;
        gap: 12px;
        position: relative;
      }

      .twb-chatbot-header-text {
        flex: 1;
        min-width: 0;
      }

      .twb-chatbot-title {
        font-family: 'Prata', serif;
        font-size: 22px;
        color: #ffffff;
        display: block;
      }

      .twb-chatbot-subtitle {
        font-size: 11px;
        color: #f0f7e0;
        display: block;
        margin-top: -2px;
      }

      .twb-chatbot-close {
        position: absolute;
        right: 16px;
        top: 50%;
        transform: translateY(-50%);
        border: none;
        background: none;
        color: #ffffff;
        font-size: 24px;
        cursor: pointer;
        line-height: 1;
      }

      .twb-chatbot-close:focus {
        outline: 2px solid #f3f9d8;
        border-radius: 50%;
      }

      .twb-chatbot-history {
        flex: 1;
        padding: 16px;
        overflow-y: auto;
        font-size: 15px;
        line-height: 1.6;
        background: #fafcf8;
      }

      .twb-chatbot-history::-webkit-scrollbar {
        width: 8px;
      }

      .twb-chatbot-history::-webkit-scrollbar-thumb {
        background: rgba(107, 124, 58, 0.4);
        border-radius: 4px;
      }

      .twb-chatbot-placeholder {
        text-align: center;
        color: #6b7c3a;
        font-size: 13px;
        padding: 20px;
        font-style: italic;
      }

      .twb-chatbot-message {
        margin-bottom: 12px;
        display: flex;
        width: 100%;
      }

      .twb-chatbot-message span {
        display: inline-block;
        padding: 12px 16px;
        border-radius: 16px;
        max-width: 85%;
        word-wrap: break-word;
        background: #f6f8f0;
        color: #355825;
      }

      .twb-chatbot-user {
        justify-content: flex-end;
      }

      .twb-chatbot-user span {
        background: #ecf1e7;
        border-radius: 16px 16px 4px 16px;
      }

      .twb-chatbot-agent span {
        border-radius: 16px 16px 16px 4px;
      }

      .twb-chatbot-typing span {
        background: #f0f3ea;
        color: #6b7c3a;
        font-style: italic;
      }

      .twb-chatbot-error span {
        background: #fbecec;
        color: #8a2727;
        border-radius: 16px 16px 16px 4px;
      }

      .twb-chatbot-form {
        display: flex;
        border-top: 1px solid #e8eeda;
        background: #f8faf2;
        min-height: 58px;
      }

      .twb-chatbot-input {
        flex: 1;
        padding: 16px 12px;
        border: none;
        background: #f8faf2;
        font-size: 15px;
        color: #355825;
      }

      .twb-chatbot-input:focus {
        outline: none;
      }

      .twb-chatbot-send {
        border: none;
        background: linear-gradient(135deg, #8a9d4c, #6b7c3a);
        color: #ffffff;
        padding: 0 24px;
        font-size: 20px;
        cursor: pointer;
        transition: opacity 0.2s ease-in-out;
      }

      .twb-chatbot-send:hover {
        opacity: 0.85;
      }

      .twb-chatbot-send:focus {
        outline: none;
      }

      @media (max-width: 768px) {
        .twb-chatbot-button {
          right: 16px;
          bottom: 16px;
          width: 56px;
          height: 56px;
        }

        .twb-chatbot-box {
          right: 16px;
          left: 16px;
          bottom: 16px;
          width: auto;
          height: 60vh;
          max-height: 60vh;
        }
      }
    `;
    document.head.appendChild(style);
  }

  const widgetBtn = document.createElement('button');
  widgetBtn.type = 'button';
  widgetBtn.className = 'twb-chatbot-button';
  widgetBtn.setAttribute('aria-label', 'Открыть чат с AI-консьержем');
  widgetBtn.setAttribute('aria-expanded', 'false');
  widgetBtn.innerHTML =
    '<span class="twb-chatbot-button-icon" aria-hidden="true">' +
    '<svg width="44" height="44" viewBox="0 0 44 44" focusable="false" aria-hidden="true">' +
    '<defs>' +
    '<linearGradient id="twbBtnGradient" x1="0%" y1="0%" x2="100%" y2="100%">' +
    '<stop offset="0%" stop-color="#8a9d4c"></stop>' +
    '<stop offset="100%" stop-color="#6b7c3a"></stop>' +
    '</linearGradient>' +
    '<linearGradient id="twbBubbleGradient" x1="15%" y1="10%" x2="85%" y2="90%">' +
    '<stop offset="0%" stop-color="#ffffff" stop-opacity="0.95"></stop>' +
    '<stop offset="100%" stop-color="#eef5d1" stop-opacity="0.9"></stop>' +
    '</linearGradient>' +
    '</defs>' +
    '<circle cx="22" cy="22" r="21" fill="url(#twbBtnGradient)"></circle>' +
    '<circle cx="22" cy="22" r="19" fill="#ffffff" fill-opacity="0.08" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1"></circle>' +
    '<path d="M31 13.5H17c-3.59 0-6.5 2.91-6.5 6.5v5.3c0 3.59 2.91 6.5 6.5 6.5h3.7l1.84 4.21c.26.59 1.15.59 1.41 0L25.8 31.8H31c3.59 0 6.5-2.91 6.5-6.5v-5.3c0-3.59-2.91-6.5-6.5-6.5Z" fill="url(#twbBubbleGradient)"></path>' +
    '<path d="M18.8 20.5h10.4" stroke="#6b7c3a" stroke-width="1.6" stroke-linecap="round" opacity="0.75"></path>' +
    '<path d="M18.8 24.5h6.8" stroke="#6b7c3a" stroke-width="1.6" stroke-linecap="round" opacity="0.65"></path>' +
    '<circle cx="30.8" cy="16.8" r="2.2" fill="#ffffff" opacity="0.95"></circle>' +
    '<circle cx="31.9" cy="15.2" r="1.2" fill="#f0f5d8" opacity="0.95"></circle>' +
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
        const errorDetail = data && typeof data.detail === 'string' && data.detail.trim()
          ? data.detail.trim()
          : '';
        const errorMessage = errorDetail
          ? `Ошибка сервера (${response.status}): ${errorDetail}`
          : `Ошибка сервера: ${response.status}`;
        throw new Error(errorMessage);
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
      const errorMessage =
        error instanceof Error && error.message
          ? error.message
          : 'Ошибка соединения с сервером. Попробуйте позже.';

      if (typingBubble) {
        typingBubble.innerHTML = `<span>${escapeHTML(errorMessage)}</span>`;
        typingBubble.className = 'twb-chatbot-message twb-chatbot-error';
      } else {
        addMessage(errorMessage, 'error');
      }

      console.error(error);
    }
  });
})();
