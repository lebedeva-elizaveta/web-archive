document.getElementById("registerForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Отменяем стандартную отправку формы для обработки через JavaScript

    const email = document.getElementById("emailInput").value;
    const password = document.getElementById("passwordInput").value;

    // Отправляем данные на сервер через fetch
    fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })  // Отправляем данные в формате JSON
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
                // Перенаправляем на страницу входа
                window.location.href = '/login';
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
            text: 'Произошла ошибка при попытке регистрации.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    });
});
