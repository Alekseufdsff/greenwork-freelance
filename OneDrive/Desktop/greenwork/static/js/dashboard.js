// Функции для личного кабинета

// Управление модальным окном вывода
function showWithdrawalModal() {
    document.getElementById('withdrawalModal').style.display = 'block';
}

function closeWithdrawalModal() {
    document.getElementById('withdrawalModal').style.display = 'none';
    document.getElementById('withdrawalMessage').innerHTML = '';
}

// Выбор способа оплаты
document.addEventListener('DOMContentLoaded', function() {
    const paymentMethods = document.querySelectorAll('.payment-method');
    if (paymentMethods.length > 0) {
        paymentMethods.forEach(method => {
            method.addEventListener('click', function() {
                document.querySelectorAll('.payment-method').forEach(m => m.classList.remove('selected'));
                this.classList.add('selected');
                document.getElementById('payment_method').value = this.dataset.method;
            });
        });
    }
});

// Отправка формы вывода
document.addEventListener('DOMContentLoaded', function() {
    const withdrawalForm = document.getElementById('withdrawalForm');
    if (withdrawalForm) {
        withdrawalForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button');
            const messageDiv = document.getElementById('withdrawalMessage');
            const formData = {
                amount: document.getElementById('amount').value,
                payment_method: document.getElementById('payment_method').value,
                card_number: document.getElementById('card_number').value,
                card_holder: document.getElementById('card_holder').value
            };

            // Валидация
            if (!formData.payment_method) {
                messageDiv.innerHTML = '<div class="error-message">❌ Выберите способ выплаты</div>';
                return;
            }

            if (parseInt(formData.amount) < 6000) {
                messageDiv.innerHTML = '<div class="error-message">❌ Минимальная сумма вывода: 6,000 ₽</div>';
                return;
            }

            submitBtn.innerHTML = '⏳ Отправка...';
            submitBtn.disabled = true;

            try {
                const response = await fetch('/request_withdrawal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (data.success) {
                    messageDiv.innerHTML = `<div class="success-message">${data.message}</div>`;
                    this.reset();
                    document.querySelectorAll('.payment-method').forEach(m => m.classList.remove('selected'));
                    document.getElementById('payment_method').value = '';
                    
                    // Обновляем баланс на странице
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    messageDiv.innerHTML = `<div class="error-message">${data.error}</div>`;
                }
            } catch (error) {
                messageDiv.innerHTML = '<div class="error-message">❌ Ошибка соединения</div>';
            } finally {
                submitBtn.innerHTML = '📨 Отправить заявку';
                submitBtn.disabled = false;
            }
        });
    }
});

// Закрытие модального окна по клику вне его
window.addEventListener('click', function(e) {
    const modal = document.getElementById('withdrawalModal');
    if (e.target === modal) {
        closeWithdrawalModal();
    }
});

// Закрытие по ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeWithdrawalModal();
    }
});