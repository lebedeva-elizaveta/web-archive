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

function openAddConfigForm() {
    const formHtml = `
        <form id="configForm" style="padding: 20px;">
            <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px;">
                <input type="text" id="configName" placeholder="Название конфига" style="padding: 8px; border: 1px solid #ccc; border-radius: 6px;">
                <input type="text" id="configUrl" placeholder="URL" style="padding: 8px; border: 1px solid #ccc; border-radius: 6px;">
            </div>

            <h2 style="text-align: left; margin-bottom: 10px;">Шаги:</h2>
            <div id="stepsContainer"></div>

            <button type="button" class="btn" onclick="addStep()">➕ Добавить шаг</button>
        </form>
    `;

    Swal.fire({
        title: 'Добавить конфиг',
        html: formHtml,
        width: '550px',
        showCancelButton: true,
        confirmButtonText: 'Сохранить',
        cancelButtonText: 'Отмена',
        willOpen: () => {
            addStep(); // добавить первый шаг

            // Делегируем обработку событий change для чекбоксов и селектов внутри шагов
            document.getElementById('stepsContainer').addEventListener('change', (e) => {
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

        },
        preConfirm: () => {
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

        // === ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА ===
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

    // === ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА ===
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
    }).then((result) => {
    if (result.isConfirmed) {
        const configData = result.value;

        fetch('/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }
            return response.json(); // если сервер возвращает JSON
        })
        .then(data => {
            console.log('Ответ от сервера:', data);
            Swal.fire('Успех!', 'Конфиг сохранён.', 'success');
        })
        .catch(error => {
            console.error('Ошибка при отправке:', error);
            Swal.fire('Ошибка!', 'Не удалось сохранить конфиг.', 'error');
        });
    }
});
}

/**
 * Добавляет новый шаг в форму с полями для элемента и действия
 */
function addStep() {
    const container = document.getElementById('stepsContainer');
    const stepDiv = document.createElement('div');
    stepDiv.className = 'step';
    stepDiv.style = `
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-bottom: 15px;
        padding: 12px 20px 20px 20px;
        border: 1px solid #ccc;
        border-radius: 8px;
        background-color: #f9f9f9;
        position: relative;
        font-family: Arial, sans-serif;
    `;

    stepDiv.innerHTML = `
        <button type="button" class="remove-step-btn" title="Удалить шаг" style="
            position: absolute;
            top: 10px;
            right: 10px;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: none;
            background-color: #ff4d4f;
            cursor: pointer;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s ease;
        ">
            <svg width="14" height="14" viewBox="0 0 14 14" xmlns="http://www.w3.org/2000/svg" stroke="white" stroke-width="2" stroke-linecap="round">
                <line x1="1" y1="1" x2="13" y2="13"/>
                <line x1="13" y1="1" x2="1" y2="13"/>
            </svg>
        </button>

        <label style="display: flex; align-items: center; gap: 8px; font-weight: bold; cursor: pointer;">
            <input type="checkbox" class="step-element-check" style="margin-right: 6px;">
            Элемент
        </label>
        <div class="step-element-fields" style="display: none; flex-direction: column; gap: 8px; margin-bottom: 15px;">
            <label style="display: flex; align-items: center; gap: 8px; font-weight: normal;">
                Искать по:
                <select class="step-element-by" style="flex-shrink: 0; width: 140px; padding: 6px; border: 1px solid #ccc; border-radius: 6px; font-size: 16px;">
                    <option value="id">id</option>
                    <option value="name">name</option>
                    <option value="xpath">xpath</option>
                    <option value="url_contains">url_contains</option>
                </select>
            </label>

            <label class="step-element-type-label" style="display: flex; align-items: center; gap: 8px; font-weight: normal;">
                Тип:
                <input class="step-element-type" type="text" placeholder="type (опционально)" style="flex-grow: 1; padding: 6px; border: 1px solid #ccc; border-radius: 6px;">
            </label>

            <label style="display: flex; align-items: center; gap: 8px; font-weight: normal;">
                Значение:
                <input class="step-element-value" type="text" placeholder="Значение" style="flex-grow: 1; padding: 6px; border: 1px solid #ccc; border-radius: 6px;">
            </label>
        </div>

        <label style="display: flex; align-items: center; gap: 8px; font-weight: bold; cursor: pointer;">
            <input type="checkbox" class="step-action-check" style="margin-right: 6px;">
            Действие
        </label>
        <div class="step-action-fields" style="display: none; flex-direction: column; gap: 8px; margin-bottom: 15px;">
            <label style="display: flex; align-items: center; gap: 8px; font-weight: normal;">
                Тип действия:
                <select class="step-action-type" style="flex-shrink: 0; width: 180px; padding: 6px; border: 1px solid #ccc; border-radius: 6px; font-size: 16px;">
                    <option value="send_keys" selected>send_keys</option>
                    <option value="click">click</option>
                    <option value="click_js">click_js</option>
                </select>
            </label>

            <label style="display: flex; align-items: center; gap: 8px; font-weight: normal;">
                Значение из:
                <select class="step-action-value-type" style="flex-shrink: 0; width: 140px; padding: 6px; border: 1px solid #ccc; border-radius: 6px; font-size: 16px;">
                    <option value="value" selected>value</option>
                    <option value="credentials">credentials</option>
                </select>
            </label>

            <input type="text" class="step-action-value" placeholder="Значение действия" style="padding: 6px; border: 1px solid #ccc; border-radius: 6px; font-size: 16px;">
            <select class="step-action-credentials-value" style="display: none; padding: 6px; border: 1px solid #ccc; border-radius: 6px; font-size: 16px;">
                <option value="">Выберите credentials</option>
                <option value="login">login</option>
                <option value="password">password</option>
                <option value="code">code</option>
            </select>
        </div>

        <label style="display: flex; align-items: center; gap: 8px; font-weight: normal;">
            <input type="checkbox" class="step-optional" style="margin-right: 6px;">
            Необязательный
        </label>
    `;

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
