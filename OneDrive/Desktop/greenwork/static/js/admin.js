// Функции для админ-панели

// Фильтрация заявок
function filterRequests(status) {
    const requests = document.querySelectorAll('.request-item');
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    // Обновляем активную кнопку
    filterBtns.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Показываем/скрываем заявки
    requests.forEach(request => {
        if (status === 'all' || request.dataset.status === status) {
            request.style.display = 'block';
            setTimeout(() => {
                request.style.opacity = '1';
                request.style.transform = 'translateY(0)';
            }, 50);
        } else {
            request.style.opacity = '0';
            request.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                request.style.display = 'none';
            }, 300);
        }
    });
}

// Обновление баланса пользователя
async function updateBalance(username) {
    const balanceInput = document.getElementById(`balance-${username}`);
    const newBalance = balanceInput.value;
    const messageDiv = document.getElementById('balanceMessage');

    // Валидация
    if (!newBalance || newBalance < 0) {
        showMessage(messageDiv, '❌ Введите корректную сумму', 'error');
        return;
    }

    try {
        const response = await fetch('/admin/update_balance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                balance: parseInt(newBalance)
            })
        });

        const data = await response.json();

        if (data.success) {
            showMessage(messageDiv, `✅ Баланс пользователя ${username} обновлен: ${newBalance} ₽`, 'success');
            
            // Анимируем обновление
            balanceInput.style.borderColor = 'var(--success)';
            setTimeout(() => {
                balanceInput.style.borderColor = '';
            }, 2000);
            
        } else {
            showMessage(messageDiv, '❌ Ошибка обновления баланса', 'error');
        }
    } catch (error) {
        showMessage(messageDiv, '❌ Ошибка соединения', 'error');
    }
}

// Обработка заявки на вывод
async function processRequest(requestId, action) {
    const requestItem = document.querySelector(`.request-item [onclick*="${requestId}"]`).closest('.request-item');
    
    // Подтверждение для отклонения
    if (action === 'rejected' && !confirm('Вы уверены, что хотите отклонить эту заявку?')) {
        return;
    }

    try {
        const response = await fetch('/admin/process_request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                request_id: requestId,
                action: action
            })
        });

        const data = await response.json();

        if (data.success) {
            // Обновляем интерфейс
            updateRequestUI(requestItem, action);
            showMessage(document.getElementById('requestsMessage'), `✅ Заявка #${requestId} обработана`, 'success');
        } else {
            showMessage(document.getElementById('requestsMessage'), '❌ Ошибка обработки заявки', 'error');
        }
    } catch (error) {
        showMessage(document.getElementById('requestsMessage'), '❌ Ошибка соединения', 'error');
    }
}

// Обновление UI заявки
function updateRequestUI(requestItem, action) {
    const statusDiv = requestItem.querySelector('.request-status');
    const actionsDiv = requestItem.querySelector('.request-actions');
    
    // Обновляем статус
    statusDiv.className = `request-status status-${action}`;
    statusDiv.innerHTML = action === 'paid' ? '✅ Выплачено' : '❌ Отклонено';
    
    // Убираем кнопки действий
    if (actionsDiv) {
        actionsDiv.style.opacity = '0';
        setTimeout(() => {
            actionsDiv.remove();
        }, 300);
    }
    
    // Добавляем мету обработки
    const metaDiv = document.createElement('div');
    metaDiv.className = 'request-meta';
    metaDiv.style.animation = 'slideUp 0.3s ease';
    metaDiv.innerHTML = `
        <div>🕒 Обработано: ${new Date().toLocaleString('ru-RU')}</div>
        <div>👨‍💼 ADMIN</div>
    `;
    requestItem.appendChild(metaDiv);
}

// Показ сообщений
function showMessage(container, message, type) {
    if (!container) return;
    
    const bgColor = type === 'success' ? 'rgba(0, 255, 0, 0.1)' : 'rgba(255, 0, 0, 0.1)';
    const borderColor = type === 'success' ? 'var(--success)' : 'var(--error)';
    
    container.innerHTML = `
        <div style="background: ${bgColor}; border: 1px solid ${borderColor}; 
                    border-radius: 8px; padding: 1rem; margin-top: 1rem; text-align: center;
                    animation: slideUp 0.3s ease;">
            ${message}
        </div>
    `;
    
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

// Поиск заявок
function searchRequests(query) {
    const requests = document.querySelectorAll('.request-item');
    const lowerQuery = query.toLowerCase();
    
    requests.forEach(request => {
        const text = request.textContent.toLowerCase();
        if (text.includes(lowerQuery)) {
            request.style.display = 'block';
        } else {
            request.style.display = 'none';
        }
    });
}

// Автоматическое обновление каждые 30 секунд
let autoRefresh = true;

function toggleAutoRefresh() {
    autoRefresh = !autoRefresh;
    const btn = document.getElementById('refreshToggle');
    if (btn) {
        btn.textContent = autoRefresh ? '🔴 Выкл. автообновление' : '🟢 Вкл. автообновление';
    }
}

if (autoRefresh) {
    setInterval(() => {
        if (autoRefresh && document.visibilityState === 'visible') {
            window.location.reload();
        }
    }, 30000);
}

// Инициализация админ-панели
document.addEventListener('DOMContentLoaded', function() {
    console.log('🛠️ Админ-панель GreenWork загружена');
});