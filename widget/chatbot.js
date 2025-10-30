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
        width: 64px;
        height: 64px;
        border: none;
        border-radius: 32px;
        background: linear-gradient(135deg, #a7c75b, #76953d);
        padding: 0;
        cursor: pointer;
        box-shadow: 0 10px 25px rgba(108, 138, 55, 0.35), 0 2px 6px rgba(41, 56, 25, 0.18);
        transition: transform 0.25s ease, box-shadow 0.25s ease, filter 0.25s ease;
        z-index: 2147483000;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .twb-chatbot-button:focus {
        outline: 2px solid #c9d99a;
        outline-offset: 3px;
      }

      .twb-chatbot-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 34px rgba(90, 119, 42, 0.38);
        filter: brightness(1.05);
      }

      .twb-chatbot-button-hidden {
        display: none !important;
      }

      .twb-chatbot-box {
        position: fixed;
        right: 24px;
        bottom: 104px;
        width: 372px;
        max-width: calc(100vw - 48px);
        height: 536px;
        max-height: 78vh;
        background: #ffffff;
        border-radius: 22px;
        box-shadow: 0 28px 60px rgba(82, 107, 32, 0.25), 0 12px 32px rgba(41, 53, 23, 0.12);
        display: none;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid rgba(142, 170, 84, 0.28);
        z-index: 2147482999;
        color: #1f2a1a;
        font-family: 'Manrope', 'Open Sans', Arial, sans-serif;
      }

      .twb-chatbot-box-visible {
        display: flex;
      }

      .twb-chatbot-header {
        background: linear-gradient(135deg, #8fb45d, #5f7e31);
        padding: 22px 64px 22px 24px;
        border-radius: 22px 22px 0 0;
        display: flex;
        align-items: center;
        gap: 12px;
        position: relative;
        box-shadow: inset 0 -1px 0 rgba(255, 255, 255, 0.25);
      }

      .twb-chatbot-header-text {
        flex: 1;
        min-width: 0;
      }

      .twb-chatbot-title {
        font-family: 'Prata', serif;
        font-size: 24px;
        color: #ffffff;
        display: block;
        letter-spacing: 0.02em;
      }

      .twb-chatbot-subtitle {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.82);
        display: block;
        margin-top: 2px;
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
        padding: 20px 22px;
        overflow-y: auto;
        font-size: 15px;
        line-height: 1.65;
        background: linear-gradient(180deg, #f7f9f3 0%, #f3f6ec 100%);
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
        border-radius: 18px;
        max-width: 85%;
        word-wrap: break-word;
        background: rgba(255, 255, 255, 0.9);
        color: #2d3a20;
        box-shadow: 0 8px 18px rgba(137, 163, 86, 0.18);
        backdrop-filter: blur(2px);
      }

      .twb-chatbot-user {
        justify-content: flex-end;
      }

      .twb-chatbot-user span {
        background: linear-gradient(135deg, #dbe8c2, #c3d89d);
        border-radius: 18px 18px 6px 18px;
      }

      .twb-chatbot-agent span {
        border-radius: 18px 18px 18px 6px;
      }

      .twb-chatbot-typing span {
        background: rgba(213, 226, 182, 0.55);
        color: #496428;
        font-style: italic;
      }

      .twb-chatbot-error span {
        background: #fbecec;
        color: #8a2727;
        border-radius: 18px 18px 18px 6px;
      }

      .twb-chatbot-form {
        display: flex;
        border-top: 1px solid rgba(150, 177, 98, 0.3);
        background: rgba(246, 250, 235, 0.92);
        min-height: 62px;
        padding: 6px 8px 6px 16px;
        gap: 8px;
        align-items: center;
      }

      .twb-chatbot-input {
        flex: 1;
        padding: 14px 16px;
        border: 1px solid rgba(122, 151, 66, 0.3);
        border-radius: 14px;
        background: #ffffff;
        font-size: 15px;
        color: #2f3c1f;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
      }

      .twb-chatbot-input::placeholder {
        color: rgba(79, 98, 46, 0.5);
      }

      .twb-chatbot-input:focus {
        outline: none;
        border-color: rgba(103, 136, 46, 0.65);
        box-shadow: 0 0 0 3px rgba(151, 187, 88, 0.25);
      }

      .twb-chatbot-send {
        border: none;
        background: linear-gradient(135deg, #88ad47, #5e7c2f);
        color: #ffffff;
        padding: 0 22px;
        font-size: 20px;
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border-radius: 14px;
        height: 48px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 12px 24px rgba(91, 123, 38, 0.25);
      }

      .twb-chatbot-send:hover {
        transform: translateY(-1px);
        box-shadow: 0 16px 28px rgba(79, 109, 33, 0.28);
      }

      .twb-chatbot-send:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(164, 204, 96, 0.4);
      }

      @media (max-width: 768px) {
        .twb-chatbot-button {
          right: 16px;
          bottom: 16px;
          width: 60px;
          height: 60px;
        }

        .twb-chatbot-box {
          right: 16px;
          left: 16px;
          bottom: 16px;
          width: auto;
          height: 64vh;
          max-height: 64vh;
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
  widgetBtn.innerHTML = `
    <span class="twb-chatbot-button-icon" aria-hidden="true">
      <svg width="48" height="48" viewBox="0 0 48 48" focusable="false" aria-hidden="true">
        <defs>
          <linearGradient id="twbBtnGradient" x1="12%" y1="8%" x2="88%" y2="92%">
            <stop offset="0%" stop-color="#a6c35c"></stop>
            <stop offset="48%" stop-color="#7f9a3f"></stop>
            <stop offset="100%" stop-color="#5c7a2d"></stop>
          </linearGradient>
          <radialGradient id="twbInnerGlow" cx="50%" cy="32%" r="64%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95"></stop>
            <stop offset="60%" stop-color="#edf5d8" stop-opacity="0.88"></stop>
            <stop offset="100%" stop-color="#cbd9a5" stop-opacity="0.65"></stop>
          </radialGradient>
          <linearGradient id="twbLetterGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#183214"></stop>
            <stop offset="100%" stop-color="#2f4d20"></stop>
          </linearGradient>
        </defs>
        <circle cx="24" cy="24" r="23" fill="url(#twbBtnGradient)"></circle>
        <circle
          cx="24"
          cy="24"
          r="20"
          fill="url(#twbInnerGlow)"
          stroke="#ffffff"
          stroke-opacity="0.35"
          stroke-width="1.1"
        ></circle>
        <path
          d="M24 6c7.7 0 14 6.3 14 14 0 6.5-4.5 12-10.7 13.6-1.2.3-1.9 1.5-1.6 2.7l.9 3.8c.3 1.4-.6 2.8-2 3.1-.3.1-.6.1-.9.1-.9 0-1.8-.4-2.3-1.2l-2.6-3.9c-.4-.6-1.1-.9-1.8-.8C11.6 37.1 6 30.9 6 23.2 6 14.6 12.9 6 24 6Z"
          fill="rgba(255, 255, 255, 0.08)"
        ></path>
        <g fill="none" stroke="#ffffff" stroke-linecap="round" stroke-opacity="0.4">
          <path d="M11.5 16.5h4.2"></path>
          <path d="M32.3 33.5h4.2"></path>
          <path d="M14.5 30.8h2.6"></path>
          <path d="M30.4 15.2h2.6"></path>
        </g>
        <g fill="url(#twbLetterGradient)">
          <path
            d="M16.6 32.5h3l1.4-4.2h8.1l1.4 4.2h3l-7-17h-2.9l-7 17Zm5.3-6.9 2.7-6.9 2.7 6.9h-5.4Z"
          ></path>
          <path d="M30.6 15.5h2.8v17h-2.8z"></path>
        </g>
        <path
          d="M24 11.6c3 0 5.7 1.7 7.1 4.2"
          fill="none"
          stroke="#f5ffe7"
          stroke-opacity="0.65"
          stroke-width="1.2"
          stroke-linecap="round"
        ></path>
      </svg>
    </span>
  `;

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
