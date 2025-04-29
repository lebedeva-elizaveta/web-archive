async function addPage() {
    const urlInput = document.getElementById("urlInput").value.trim();
    const isProtected = document.getElementById("protectedPageCheckbox").checked;

    if (!urlInput) {
        Swal.fire('Ошибка!', 'Введите URL.', 'error');
        return;
    }

    let needAuthWindow = false;
    let unsupportedSite = false;

    const isBRS = urlInput.includes("cs");
    const isMoodle = urlInput.includes("edu");
    const isVK = urlInput.includes("vk");

    if (!isBRS && !isMoodle && !isVK && isProtected) {
        unsupportedSite = true;
    }

    if (unsupportedSite) {
        Swal.fire('Ошибка!', 'Пока поддерживаются только ВК, БРС и Moodle.', 'error');
        return;
    }

    try {
        if (isProtected) {
            if (isBRS || isMoodle) {
                Swal.fire({
                    title: 'Проверка авторизации...',
                    allowOutsideClick: false,
                    didOpen: () => Swal.showLoading()
                });

                if (isBRS) {
                    const response = await fetch('/auth/check?type=brs');
                    const authData = await response.json();
                    if (authData.need_auth) needAuthWindow = true;
                } else if (isMoodle) {
                    const response = await fetch('/auth/check?type=moodle');
                    const authData = await response.json();
                    if (authData.need_auth) needAuthWindow = true;
                }

                Swal.close();
            } else if (isVK) {
                needAuthWindow = true;
            }
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

    fetch(`/view_domain_info/${encodeURIComponent(urlInput)}`)
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
