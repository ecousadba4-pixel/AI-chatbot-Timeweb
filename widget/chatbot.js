(function () {
  const widget = document.querySelector('.twb-chatbot');
  if (!widget) return;

  const messagesContainer = widget.querySelector('#twb-messages');
  const form = widget.querySelector('#twb-form');
  const input = widget.querySelector('#twb-input');
  const apiEndpoint = widget.dataset.apiEndpoint;
  const sessionId = crypto.randomUUID();

  function appendMessage(role, text) {
    const bubble = document.createElement('div');
    bubble.classList.add('twb-bubble', `twb-${role}`);
    bubble.innerText = text;
    messagesContainer.appendChild(bubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (!question) return;

    appendMessage('user', question);
    input.value = '';
    appendMessage('agent', 'Думаю над ответом...');

    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, session_id: sessionId }),
      });
      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }
      const data = await response.json();
      const placeholders = messagesContainer.querySelectorAll('.twb-agent');
      const lastBubble = placeholders[placeholders.length - 1];
      if (lastBubble) {
        lastBubble.innerText = data.answer;
      }
    } catch (error) {
      const placeholders = messagesContainer.querySelectorAll('.twb-agent');
      const lastBubble = placeholders[placeholders.length - 1];
      if (lastBubble) {
        lastBubble.innerText =
          'Произошла ошибка при получении ответа. Пожалуйста, попробуйте позже.';
      }
      console.error(error);
    }
  });
})();
