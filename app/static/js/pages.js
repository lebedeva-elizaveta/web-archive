let sortedPages = [];
const itemsPerPage = 10;
let currentPage = 1;
let currentSortOrder = 'desc';

function sortPages(order) {
    sortedPages = [...archivedPages].sort((a, b) => {
        const dateA = new Date(a.timestamp);
        const dateB = new Date(b.timestamp);
        return order === 'asc' ? dateA - dateB : dateB - dateA;
    });
}

function changeSortOrder(order) {
    currentSortOrder = order;
    sortPages(order);
    currentPage = 1;
    renderPage(currentPage);
}

function renderPagination(totalPages) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        const pageLink = document.createElement('a');
        pageLink.textContent = i;
        pageLink.href = '#';
        pageLink.onclick = (function (page) {
            return function (event) {
                event.preventDefault();
                currentPage = page;
                renderPage(page);
            };
        })(i);

        const pageItem = document.createElement('li');
        if (i === currentPage) {
            pageLink.style.fontWeight = 'bold';
        }
        pageItem.appendChild(pageLink);
        pagination.appendChild(pageItem);
    }
}

function renderPage(page) {
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = page * itemsPerPage;
    const pagesList = document.getElementById('pagesList');

    pagesList.innerHTML = '';
    const currentItems = sortedPages.slice(startIndex, endIndex);

    currentItems.forEach((page, index) => {
        const li = document.createElement('li');
        const date = new Date(page.timestamp);
        const formattedDate = date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        li.innerHTML = `
            <div class="version-info-container">
                <div class="version-info">
                    <a href="/show/page/${page.id}">
                        Версия ${startIndex + index + 1} — ${formattedDate}
                    </a>
                </div>
                <button class="show-info-button" onclick="toggleDomainInfo(this, ${page.id})">
                    Информация о домене
                </button>
            </div>
            <div id="domainInfoArea-${page.id}" class="domain-info"></div>
        `;
        pagesList.appendChild(li);
    });

    renderPagination(Math.ceil(sortedPages.length / itemsPerPage));
}

function toggleDomainInfo(button, pageId) {
    const domainInfoArea = document.getElementById(`domainInfoArea-${pageId}`);

    if (domainInfoArea.style.display === 'none' || domainInfoArea.innerHTML === '') {
        fetch(`/show/info/${pageId}`)
            .then(response => response.text())
            .then(html => {
                domainInfoArea.innerHTML = html;
                domainInfoArea.style.display = 'block';
                button.textContent = 'Скрыть информацию о домене';
            })
            .catch(error => console.error('Error:', error));
    } else {
        domainInfoArea.style.display = 'none';
        domainInfoArea.innerHTML = '';
        button.textContent = 'Информация о домене';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    sortPages(currentSortOrder);        // Сначала сортируем
    renderPage(currentPage);            // Потом рендерим нужную страницу
});

