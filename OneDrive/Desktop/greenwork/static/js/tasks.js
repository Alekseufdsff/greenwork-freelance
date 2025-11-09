// Функции для страницы заданий

// Выполнение задания
async function completeTask(taskIndex, reward) {
    const taskCard = document.getElementById(`task-${taskIndex}`);
    const button = taskCard.querySelector('.complete-task');
    const messageDiv = document.getElementById(`task-message-${taskIndex}`);

    // Блокируем кнопку и показываем загрузку
    button.innerHTML = '⏳ Выполняется...';
    button.disabled = true;
    taskCard.classList.add('loading');

    try {
        const response = await fetch('/complete_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            // Показываем успешное сообщение
            messageDiv.innerHTML = `
                <div class="completion-message">
                    ✅ Задание выполнено! +${data.reward} ₽<br>
                    💰 Новый баланс: ${data.balance} ₽
                </div>
            `;

            // Обновляем статистику
            updateStats(data.completed_tasks, data.total_earned);

            // Анимируем награду
            button.innerHTML = '✅ Выполнено';
            button.classList.remove('btn-primary');
            button.classList.add('btn-success');
            
            // Добавляем анимацию пульсации
            taskCard.classList.add('pulse');
            
            // Обновляем страницу через 3 секунды для новых заданий
            setTimeout(() => {
                window.location.reload();
            }, 3000);

        } else {
            showError(messageDiv, button, taskCard, '❌ Ошибка выполнения задания');
        }

    } catch (error) {
        console.error('Ошибка:', error);
        showError(messageDiv, button, taskCard, '❌ Ошибка соединения');
    }
}

// Обновление статистики
function updateStats(completedTasks, totalEarned) {
    const completedEl = document.getElementById('completedTasks');
    const earnedEl = document.getElementById('totalEarned');
    
    if (completedEl) completedEl.textContent = completedTasks;
    if (earnedEl) earnedEl.textContent = totalEarned + ' ₽';
}

// Показ ошибки
function showError(messageDiv, button, taskCard, message) {
    messageDiv.innerHTML = `<div style="color: var(--error); text-align: center; margin-top: 1rem;">${message}</div>`;
    button.innerHTML = '🎯 Выполнить задание';
    button.disabled = false;
    taskCard.classList.remove('loading');
}

// Загрузка статистики
async function loadStats() {
    try {
        // В реальном приложении здесь был бы запрос к API
        // Для демо используем фиктивные данные из data-атрибутов
        const statsEl = document.getElementById('statsData');
        if (statsEl) {
            const completed = statsEl.dataset.completed || 0;
            const earned = statsEl.dataset.earned || 0;
            updateStats(completed, earned);
        }
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    
    // Добавляем анимацию при наведении на карточки
    const taskCards = document.querySelectorAll('.task-card');
    taskCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
});