document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Отменяем стандартную отправку формы для обработки через JavaScript

    const email = document.getElementById("emailInput").value;
    const password = document.getElementById("passwordInput").value;

    // Отправляем данные на сервер через fetch
    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json" // Указываем, что данные будут в формате JSON
        },
        body: JSON.stringify({ email, password })  // Сериализуем данные в формат JSON
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                title: 'Успех!',
                text: data.message,
                icon: 'success',
                confirmButtonText: 'OK'
            }).then(() => {
                // Перенаправляем на главную страницу
                window.location.href = '/';  // Например, на домашнюю страницу
            });
        } else {
            Swal.fire({
                title: 'Ошибка!',
                text: data.message,
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    })
    .catch(error => {
        console.error("Ошибка:", error);
        Swal.fire({
            title: 'Ошибка!',
            text: 'Произошла ошибка при попытке входа.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    });
});
