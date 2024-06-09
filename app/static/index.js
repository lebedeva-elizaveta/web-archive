function addPage() {
    var urlInput = document.getElementById('urlInput').value;
    fetch('/archive', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: urlInput }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message);
        } else {
            showErrorMessage(data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function showPage() {
    var urlInput = document.getElementById('urlInput').value;
    if (!urlInput) {
        showErrorMessage('Введите URL');
        return;
    }

    var encodedUrl = encodeURIComponent(urlInput);
    window.location.href = '/view/' + encodedUrl;
}

function showDomainInfo() {
    var urlInput = document.getElementById('urlInput').value;
    if (!urlInput) {
        showErrorMessage('Введите URL');
        return;
    }
    fetch('/view_domain_info/' + encodeURIComponent(urlInput))
        .then(response => response.text())
        .then(html => {
            document.getElementById('displayArea').innerHTML = html;
        })
        .catch(error => console.error('Error:', error));
}

function toggleDomainInfo() {
    var displayArea = document.getElementById('displayArea');
    var domainInfoButton = document.getElementById('domainInfoButton');
    var urlInput = document.getElementById('urlInput').value;
    if (!urlInput) {
        showErrorMessage('Введите URL');
        return;
    }
    if (displayArea.style.display === 'none') {
        displayArea.style.display = 'block';
        domainInfoButton.textContent = 'Скрыть информацию о домене';
        showDomainInfo();
    } else {
        displayArea.style.display = 'none';
        domainInfoButton.textContent = 'Показать информацию о домене';
    }
}

function logout() {
    fetch('/logout', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/login';
        } else {
            showErrorMessage(data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function showSuccessMessage(message) {
    var flashMessage = document.createElement('div');
    flashMessage.classList.add('flash-message', 'success');
    flashMessage.textContent = message;
    document.querySelector('.container').insertBefore(flashMessage, document.querySelector('form'));
    setTimeout(function() {
        flashMessage.remove();
    }, 3000);
}

function showErrorMessage(message) {
    var flashMessage = document.createElement('div');
    flashMessage.classList.add('flash-message', 'error');
    flashMessage.textContent = message;
    document.querySelector('.container').insertBefore(flashMessage, document.querySelector('form'));
    setTimeout(function() {
        flashMessage.remove();
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    var displayArea = document.getElementById('displayArea');
    displayArea.style.display = 'none';
});

document.addEventListener('DOMContentLoaded', function() {
    var flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.remove();
        }, 3000);
    });
});
