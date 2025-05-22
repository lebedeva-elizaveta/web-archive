async function addPage() {
    const urlInput = document.getElementById("urlInput").value.trim();
    const isProtected = document.getElementById("protectedPageCheckbox").checked;

    if (!urlInput) {
        Swal.fire('Ошибка!', 'Введите URL.', 'error');
        return;
    }

    let needAuthWindow = false;

    try {
        if (isProtected) {
            Swal.fire({
                title: 'Проверка авторизации...',
                allowOutsideClick: false,
                didOpen: () => Swal.showLoading()
            });

            // Запрашиваем без передачи type — бэкенд сам определит
            const response = await fetch('/auth/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: urlInput }) // передаем url, чтобы бэк знал что проверять
            });

            const authData = await response.json();

            if (authData.need_auth) needAuthWindow = true;

            Swal.close();
        }
    } catch (error) {
        console.error("Ошибка при проверке авторизации:", error);
        Swal.close();
        Swal.fire('Ошибка!', 'Ошибка при проверке авторизации.', 'error');
        return;
    }

    if (needAuthWindow) {
        Swal.fire({
            title: 'Введите данные для авторизации',
            html: `
                <input id="swal-login" class="swal2-input" placeholder="Логин">
                <input id="swal-password" type="password" class="swal2-input" placeholder="Пароль">
                <input id="swal-code" class="swal2-input" placeholder="Код (если ВК)">
            `,
            confirmButtonText: 'Отправить',
            focusConfirm: false,
            preConfirm: () => {
                return {
                    login: document.getElementById('swal-login').value,
                    password: document.getElementById('swal-password').value,
                    code: document.getElementById('swal-code').value
                };
            }
        }).then((result) => {
            if (result.isConfirmed) {
                const credentials = result.value;
                sendAddPageRequest(urlInput, isProtected, credentials);
            }
        });
    } else {
        sendAddPageRequest(urlInput, isProtected);
    }
}

function sendAddPageRequest(urlInput, isProtected, credentials = null) {
    const data = {
        url: urlInput,
        protected: isProtected,
        credentials: credentials
    };

    Swal.fire({
        title: 'Сохраняем страницу...',
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading()
    });

    fetch("/archive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            Swal.close();
            if (data.success) {
                Swal.fire('Успех!', 'Страница добавлена!', 'success');
            } else {
                Swal.fire('Ошибка!', data.error || 'Ошибка при добавлении страницы.', 'error');
            }
        })
        .catch(error => {
            Swal.close();
            console.error("Ошибка:", error);
            Swal.fire('Ошибка!', 'Что-то пошло не так!', 'error');
        });
}

function toggleDomainInfo() {
    const domainInfoButton = document.getElementById("domainInfoButton");
    const displayArea = document.getElementById("displayArea");
    const urlInput = document.getElementById("urlInput").value.trim();

    if (!urlInput) {
        Swal.fire('Ошибка!', 'Введите URL для получения информации о домене.', 'error');
        return;
    }

    if (displayArea.style.display === 'block') {
        displayArea.style.display = 'none';
        domainInfoButton.innerText = 'Показать информацию о домене';
        return;
    }

    Swal.fire({
        title: 'Загружаем информацию о домене...',
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading()
    });

    fetch(`/view/info/${encodeURIComponent(urlInput)}`)
        .then(response => response.text())
        .then(data => {
            Swal.close();
            displayArea.innerHTML = data;
            displayArea.style.display = 'block';
            domainInfoButton.innerText = 'Скрыть информацию о домене';
        })
        .catch(error => {
            Swal.close();
            console.error("Ошибка при загрузке информации о домене:", error);
            Swal.fire('Ошибка!', 'Не удалось загрузить информацию о домене.', 'error');
        });
}

function logout() {
    fetch('/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    title: 'Выход',
                    text: data.message,
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then(() => {
                    window.location.href = '/login';
                });
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            Swal.fire({
                title: 'Ошибка!',
                text: 'Произошла ошибка при выходе.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        });
}

function showPage() {
    const urlInput = document.getElementById('urlInput').value;
    if (!urlInput) {
        Swal.fire('Ошибка!', 'Введите URL.', 'error');
        return;
    }
    const encodedUrl = encodeURIComponent(urlInput);
    window.location.href = `/view/${encodedUrl}`;
}

// Загрузка HTML формы
async function fetchFormHtml(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Ошибка загрузки: ${response.status}`);
    return await response.text();
}

// Открытие модального окна с правилами
async function openRules() {
    try {
        const rulesHtml = await fetchFormHtml('/static/html/rules.html');
        await Swal.fire({
            title: 'Правила добавления конфига',
            html: rulesHtml,
            icon: 'info',
            width: '650px',
            confirmButtonText: 'Понятно',
            scrollbarPadding: false,
        });
        openAddConfigForm();
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Ошибка',
            text: 'Не удалось загрузить правила. Попробуйте позже.'
        });
        console.error('Ошибка загрузки правил:', error);
    }
}

// Установка обработчиков внутри формы
function setupFormHandlers() {
    // Кнопка "Правила"
    const rulesBtn = document.getElementById('rulesBtn');
    if (rulesBtn) {
        rulesBtn.addEventListener('click', openRules);
    }

    // Делегирование событий изменения внутри stepsContainer
    const stepsContainer = document.getElementById('stepsContainer');
    if (stepsContainer) {
        stepsContainer.addEventListener('change', (e) => {
            const target = e.target;
            const step = target.closest('.step');
            if (!step) return;

            if (target.classList.contains('step-element-check')) {
                const elementFields = step.querySelector('.step-element-fields');
                elementFields.style.display = target.checked ? 'flex' : 'none';
            }
            if (target.classList.contains('step-action-check')) {
                const actionFields = step.querySelector('.step-action-fields');
                actionFields.style.display = target.checked ? 'flex' : 'none';

                if (!target.checked) {
                    const actionTypeSelect = step.querySelector('.step-action-type');
                    const actionValueTypeSelect = step.querySelector('.step-action-value-type');
                    if (actionTypeSelect) actionTypeSelect.value = 'send_keys';
                    if (actionValueTypeSelect) actionValueTypeSelect.value = 'value';
                    updateActionValueVisibility(step);
                } else {
                    updateActionValueVisibility(step);
                }
            }
            if (target.classList.contains('step-action-type') || target.classList.contains('step-action-value-type')) {
                updateActionValueVisibility(step);
            }
        });
    }
}

// Валидация и сбор данных из формы
function validateAndCollectData() {
    const name = document.getElementById('configName').value.trim();
    const url = document.getElementById('configUrl').value.trim();

    if (!name) {
        Swal.showValidationMessage('Введите название конфига');
        return false;
    }
    if (!url) {
        Swal.showValidationMessage('Введите URL');
        return false;
    }

    const stepsElems = document.querySelectorAll('.step');
    if (stepsElems.length === 0) {
        Swal.showValidationMessage('Добавьте хотя бы один шаг');
        return false;
    }

    const steps = [];
    for (const step of stepsElems) {
        const elementChecked = step.querySelector('.step-element-check').checked;
        const actionChecked = step.querySelector('.step-action-check').checked;

        if (!elementChecked && !actionChecked) {
            Swal.showValidationMessage('В шаге должен быть выбран элемент или действие');
            return false;
        }

        let elementObj = null;
        let elementBy = null;

        if (elementChecked) {
            elementBy = step.querySelector('.step-element-by').value;
            const elementType = step.querySelector('.step-element-type').value.trim();
            const elementValue = step.querySelector('.step-element-value').value.trim();

            if (!elementBy) {
                Swal.showValidationMessage('Выберите, как искать элемент (by)');
                return false;
            }
            if (!elementValue) {
                Swal.showValidationMessage('Введите значение для элемента');
                return false;
            }

            elementObj = {
                by: elementBy,
                type: elementType || undefined,
                value: elementValue
            };
        }

        let actionObj = null;
        if (actionChecked) {
            const actionType = step.querySelector('.step-action-type').value;
            const actionValueType = step.querySelector('.step-action-value-type').value;

            if (!actionType) {
                Swal.showValidationMessage('Выберите тип действия');
                return false;
            }

            if ((actionType === 'click' || actionType === 'click_js') && !elementChecked) {
                Swal.showValidationMessage('Для действия "click" или "click_js" необходимо выбрать элемент');
                return false;
            }

            let actionValue = null;
            if (actionType !== 'click' && actionType !== 'click_js') {
                if (actionValueType === 'credentials') {
                    actionValue = step.querySelector('.step-action-credentials-value').value;
                    if (!actionValue) {
                        Swal.showValidationMessage('Выберите значение credentials');
                        return false;
                    }
                } else {
                    actionValue = step.querySelector('.step-action-value').value.trim();
                    if (!actionValue) {
                        Swal.showValidationMessage('Введите значение для действия');
                        return false;
                    }
                }
            }

            actionObj = { type: actionType };
            if (actionType !== 'click' && actionType !== 'click_js') {
                if (actionValueType === 'credentials') {
                    actionObj.value_from_credentials = actionValue;
                } else {
                    actionObj.value = actionValue;
                }
            }
        }

        if (elementChecked && ['id', 'name', 'xpath'].includes(elementBy) && !actionChecked) {
            Swal.showValidationMessage('Если выбрано id, name или xpath, необходимо выбрать действие');
            return false;
        }

        const optional = step.querySelector('.step-optional')?.checked || false;

        const stepObj = { optional };
        if (elementObj) stepObj.element = elementObj;
        if (actionObj) stepObj.action = actionObj;

        steps.push(stepObj);
    }

    return { name, url, steps };
}

// Отправка данных на сервер
async function sendConfigData(configData) {
    try {
        const response = await fetch('/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(configData)
        });

        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`);
        }

        const data = await response.json();
        console.log('Ответ от сервера:', data);
        Swal.fire('Успех!', 'Конфиг сохранён.', 'success');
    } catch (error) {
        console.error('Ошибка при отправке:', error);
        Swal.fire('Ошибка!', 'Не удалось сохранить конфиг.', 'error');
    }
}

// Основная функция открытия формы добавления конфига
async function openAddConfigForm() {
    try {
        const formHtml = await fetchFormHtml('/static/html/form.html');

        Swal.fire({
            title: 'Добавить конфиг',
            html: formHtml,
            width: '550px',
            showCancelButton: true,
            confirmButtonText: 'Сохранить',
            cancelButtonText: 'Отмена',
            didOpen: () => {
                addStep();  // Добавить первый шаг
                setupFormHandlers();
            },
            preConfirm: () => {
                return validateAndCollectData();
            }
        }).then((result) => {
            if (result.isConfirmed) {
                sendConfigData(result.value);
            }
        });
    } catch (error) {
        console.error('Ошибка при открытии формы:', error);
        Swal.fire('Ошибка!', 'Не удалось загрузить форму.', 'error');
    }
}

async function loadStepTemplate() {
    const response = await fetch('static/html/step.html');
    if (!response.ok) {
        throw new Error('Не удалось загрузить шаблон шага');
    }
    return await response.text();
}

/**
 * Добавляет новый шаг в форму с полями для элемента и действия
 */
async function addStep() {
    const container = document.getElementById('stepsContainer');
    const stepDiv = document.createElement('div');
    stepDiv.className = 'step';

    const templateHTML = await loadStepTemplate();
    stepDiv.innerHTML = templateHTML;

    container.appendChild(stepDiv);

    // Кнопка удаления шага
    stepDiv.querySelector('.remove-step-btn').onclick = () => {
        stepDiv.remove();
    };

    const actionCheck = stepDiv.querySelector('.step-action-check');
    const elementCheck = stepDiv.querySelector('.step-element-check');
    const elementFields = stepDiv.querySelector('.step-element-fields');
    const actionFields = stepDiv.querySelector('.step-action-fields');

    elementCheck.checked = false;
    elementFields.style.display = 'none';

    actionCheck.checked = false;
    actionFields.style.display = 'none';

    const actionTypeSelect = stepDiv.querySelector('.step-action-type');
    const actionValueTypeSelect = stepDiv.querySelector('.step-action-value-type');
    actionTypeSelect.value = 'send_keys';
    actionValueTypeSelect.value = 'value';

    updateActionValueVisibility(stepDiv);

    // Добавляем обработчик на селект "Искать по:"
    const elementBySelect = stepDiv.querySelector('.step-element-by');
    const typeLabel = stepDiv.querySelector('.step-element-type-label');

    function updateTypeVisibility() {
        // Если выбрано id, name или url_contains — скрываем label с input type
        const val = elementBySelect.value;
        if (val === 'id' || val === 'name' || val === 'url_contains') {
            typeLabel.style.display = 'none';
        } else {
            typeLabel.style.display = 'flex';
        }
    }

    elementBySelect.addEventListener('change', updateTypeVisibility);

    // Вызовем один раз при создании, чтобы сразу показать/скрыть
    updateTypeVisibility();
}

/**
 * Обновляет видимость полей ввода значения действия в зависимости от типа действия и выбора
 * @param {HTMLElement} stepDiv
 */
function updateActionValueVisibility(step) {
    const actionCheck = step.querySelector('.step-action-check');
    if (!actionCheck || !actionCheck.checked) {
        // Если действие не выбрано — скрываем всё, связанное с action value
        hideActionValueFields(step);
        return;
    }

    const actionTypeSelect = step.querySelector('.step-action-type');
    const actionValueTypeSelect = step.querySelector('.step-action-value-type');
    const valueFromLabel = step.querySelector('label:has(select.step-action-value-type)');
    const actionValueInput = step.querySelector('.step-action-value');
    const actionCredentialsSelect = step.querySelector('.step-action-credentials-value');

    if (!actionTypeSelect) return;

    const actionType = actionTypeSelect.value;
    const actionValueType = actionValueTypeSelect ? actionValueTypeSelect.value : 'value';

    // Если действие click или click_js — НЕ показываем "Значение из:" и связанные поля
    if (actionType === 'click' || actionType === 'click_js') {
        if (valueFromLabel) valueFromLabel.style.display = 'none';
        if (actionValueInput) actionValueInput.style.display = 'none';
        if (actionCredentialsSelect) actionCredentialsSelect.style.display = 'none';
        return;
    }

    // Иначе показываем лейбл "Значение из:"
    if (valueFromLabel) valueFromLabel.style.display = 'flex';

    // Показываем либо инпут, либо селект credentials в зависимости от выбора
    if (actionValueType === 'credentials') {
        if (actionValueInput) actionValueInput.style.display = 'none';
        if (actionCredentialsSelect) actionCredentialsSelect.style.display = 'block';
    } else {
        if (actionValueInput) actionValueInput.style.display = 'block';
        if (actionCredentialsSelect) actionCredentialsSelect.style.display = 'none';
    }
}

// Вспомогательная функция скрытия всех полей значений действия
function hideActionValueFields(step) {
    const valueFromLabel = step.querySelector('label:has(select.step-action-value-type)');
    const actionValueInput = step.querySelector('.step-action-value');
    const actionCredentialsSelect = step.querySelector('.step-action-credentials-value');

    if (valueFromLabel) valueFromLabel.style.display = 'none';
    if (actionValueInput) actionValueInput.style.display = 'none';
    if (actionCredentialsSelect) actionCredentialsSelect.style.display = 'none';
}
