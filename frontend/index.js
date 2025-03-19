// document.addEventListener("DOMContentLoaded", function () {
//     const form = document.querySelector("form");
//     const modal = document.getElementById("successModal");
//     const closeModal = document.getElementById("closeModal");
//
//     form.addEventListener("submit", async function (event) {
//         event.preventDefault(); // Отменяем стандартную отправку формы
//
//         // Формируем объект с данными
//         const requestData = {
//             restName: form.querySelector("#name-rest select").value,
//             numberOfVisitsFrom: parseInt(form.querySelectorAll("#visits input")[0].value, 10) || null,
//             numberOfVisitsTo: parseInt(form.querySelectorAll("#visits input")[1].value, 10) || null,
//             dateVisitFrom: form.querySelectorAll("#date-visit input")[0].value || null,
//             dateVisitTo: form.querySelectorAll("#date-visit input")[1].value || null,
//             textMessage: form.querySelector("#input-message-text").value.trim(),
//             linkImage: form.querySelector("#link-image input").value.trim(),
//             textButton: form.querySelectorAll(".button-tg input")[0].value.trim() || null,
//             linkButton: form.querySelectorAll(".button-tg input")[1].value.trim() || null,
//             timeToStartSending: form.querySelector("input[type='datetime-local']").value || null
//         };
//
//         console.log("Отправка данных:", requestData); // Выводим в консоль для отладки
//
//         try {
//             const response = await fetch("http://127.0.0.1:8000/api/send", {  // Замените URL на ваш
//                 method: "POST",
//                 headers: {
//                     "Content-Type": "application/json"
//                 },
//                 body: JSON.stringify(requestData)
//             });
//
//             if (!response.ok) {
//                 throw new Error(`Ошибка: ${response.statusText}`);
//             }
//
//             form.reset(); // Очистка формы
//             const result = await response.json();
//             console.log("Ответ от сервера:", result);
//
//             // Показать модальное окно
//             modal.style.visibility = "visible";
//             modal.style.opacity = "1";
//         } catch (error) {
//             console.error("Ошибка при отправке запроса:", error);
//             alert("Ошибка при отправке данных!");
//         }
//     });
//
//     // Закрытие модального окна
//     closeModal.addEventListener("click", function () {
//         modal.style.opacity = "0";
//         setTimeout(() => {
//             modal.style.visibility = "hidden";
//         }, 300);
//     });
// });
let verificationCode = null;

const formSenderWindow = document.getElementById('header')
const showRessendersWindow = document.getElementById('show-ressenders')
const menuWindow = document.getElementById('menu')
const buttonCreateRes = document.getElementById('create-res')
const buttonShowRes = document.getElementById('show-res')
const myRessButton = document.getElementById('my-res')
const buttonNewRes = document.getElementById('create-resend-button')


const modal = document.getElementById("successModal");
const closeModal = document.getElementById("closeModal");

const phoneModal = document.getElementById("phoneModal");

const phoneBlock = document.getElementById('phone')
const phoneInput = document.getElementById("phoneInput");
const phoneSubmit = document.getElementById("phoneSubmit");
const phoneAlert = document.getElementById('phone-alert')


const phoneNotFound =document.getElementById('phone-not-found-alert')

const verificationCodeBlock = document.getElementById('code-form')
const verificationInput = document.getElementById('codeInput')
const verificationSubmit = document.getElementById('codeSubmit')
const verificationCodeAlert = document.getElementById('code-alert')

const verificationSuccess = document.getElementById('verification-success')



function loadTableData() {
    // fetch("http://127.0.0.1:5057/get-sends", {
    fetch("https://sending.synergy-api.online/get-sends", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: phoneInput.value.trim() }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success && Array.isArray(data.list)) { // Ожидаем список в `data.list`
                createTable(data.list);
            } else {
                console.log("Ошибка: некорректный формат данных");
            }
        })
        .catch((error) => {
            console.error("Ошибка:", error);
            alert("Не удалось получить список рассылок.");
        });
}

function formatDate(dateString) {
    if (!dateString) return ""; // Если нет даты, вернуть пустую строку

    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString; // Если дата невалидная, вернуть как есть

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");

    // Проверяем, есть ли в строке время
    const hasTime = dateString.includes(":");

    if (hasTime) {
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    }

    return `${year}-${month}-${day}`;
}

function createTable(data) {
    if (data.length > 0){
        const container = document.getElementById("show-ressender");
        container.style.display = "block";

        let oldWrapper = document.getElementById("sendersTable-container");
        if (oldWrapper) oldWrapper.remove();

        const wrapper = document.createElement("div");
        wrapper.id = "sendersTable-container";

        const table = document.createElement("table");
        table.id = "sendersTable";

        const headers = Object.keys(data[0] || {});
        const thead = document.createElement("thead");
        const headRow = document.createElement("tr");

        headers.forEach(header => {
            const th = document.createElement("th");
            th.textContent = header;
            headRow.appendChild(th);
        });

        thead.appendChild(headRow);
        table.appendChild(thead);

        const tbody = document.createElement("tbody");
        data.forEach(item => {
            const row = document.createElement("tr");

            headers.forEach(header => {
                const td = document.createElement("td");

                if (header.toLowerCase().includes("дата")) {
                    td.textContent = formatDate(item[header]);
                } else {
                    td.textContent = item[header] || "";
                }

                row.appendChild(td);
            });

            // Создаем кнопку "Удалить"
            const deleteButton = document.createElement("button");
            deleteButton.className = "delete-btn";
            deleteButton.textContent = "Удалить";
            deleteButton.onclick = () => deleteRow(row, item.id); // Передаем ID для запроса

            const tdButton = document.createElement("td");
            tdButton.appendChild(deleteButton);
            row.appendChild(tdButton);

            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        wrapper.appendChild(table);
        container.appendChild(wrapper);
    }else{
        const container = document.getElementById("ressenders");
        container.textContent = "У вас пока нет запланированных рассылок...";
    }

}

// Функция для отправки POST запроса и удаления строки
function deleteRow(row, id) {

    id = row.cells.item(0).textContent
    // fetch("http://127.0.0.1:5057/delete-send", {
    fetch("https://sending.synergy-api.online/delete-send", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ id: id })

        // Отправляем ID в теле запроса
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Запись успешно удалена");
                row.remove(); // Удаляем строку из таблицы
            } else {
                console.log("Ошибка при удалении");
            }
        })
        .catch((error) => {
            console.error("Ошибка:", error);
            alert("Не удалось удалить запись.");
        });
}

// function createTable(data) {
//     const container = document.getElementById("show-ressenders");
//     container.style.display = "block";
//
//     let oldWrapper = document.getElementById("sendersTable-container");
//     if (oldWrapper) oldWrapper.remove();
//
//     const wrapper = document.createElement("div");
//     wrapper.id = "sendersTable-container";
//
//     const table = document.createElement("table");
//     table.id = "sendersTable";
//
//     const headers = Object.keys(data[0] || {});
//     const thead = document.createElement("thead");
//     const headRow = document.createElement("tr");
//
//     headers.forEach(header => {
//         const th = document.createElement("th");
//         th.textContent = header;
//         headRow.appendChild(th);
//     });
//
//     thead.appendChild(headRow);
//     table.appendChild(thead);
//
//     const tbody = document.createElement("tbody");
//     data.forEach(item => {
//         const row = document.createElement("tr");
//         headers.forEach(header => {
//             const td = document.createElement("td");
//
//             if (header.toLowerCase().includes("дата")) {
//                 td.textContent = formatDate(item[header]);
//             } else {
//                 td.textContent = item[header] || "";
//             }
//
//             row.appendChild(td);
//         });
//         tbody.appendChild(row);
//     });
//
//     table.appendChild(tbody);
//     wrapper.appendChild(table);
//     container.appendChild(wrapper);
//
// }


document.addEventListener('click', (event) => {
    if (event.target === buttonCreateRes) {
        menuWindow.style.display = 'none';
        formSenderWindow.style.display = 'block';
    }
    if (event.target === buttonShowRes) {
        menuWindow.style.display = 'none';
        showRessendersWindow.style.display = 'block';

        loadTableData()
    }

    if  (event.target === myRessButton) {
        formSenderWindow.style.display = 'none';
        showRessendersWindow.style.display = 'block';

        loadTableData()

    }

    if (event.target === buttonNewRes) {
        formSenderWindow.style.display = 'block';
        showRessendersWindow.style.display = 'none';
    }

})

// Показываем модальное окно при загрузке страницы
phoneModal.style.visibility = "visible";
phoneModal.style.opacity = "1";

// Обработчик для ввода номера телефона
phoneSubmit.addEventListener("click", function () {
    let phoneNumber = phoneInput.value.trim();

    if (!phoneNumber || !/^\+?\d{10,15}$/.test(phoneNumber)) {
        // alert("Введите корректный номер телефона!");
        phoneAlert.style.display = 'block';
        return;
    }

// Если номер начинается с '0', добавляем '38' перед ним
    if (phoneNumber.startsWith('0')) {
        phoneNumber = '38' + phoneNumber;

    }

    verificationCode = Math.floor(1000 + Math.random() * 9000); // Генерация 4-значного кода
//    console.log(verificationCode)
    fetch("https://sending.synergy-api.online/send-code", {
    // fetch("https://synergy-api.online/send-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: phoneNumber, code: verificationCode }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                // idTg = data.id_tg
                // alert("Код отправлен!");
                phoneBlock.style.display = 'none'
                verificationCodeBlock.style.display = 'block'
            } else {
                console.log(data)
                phoneBlock.style.display  = 'none'
                phoneNotFound.style.display = 'block'
                // alert("Ошибка при отправке кода.");
            }
        })
        .catch((error) => {
            console.error("Ошибка:", error);
            alert("Не удалось отправить код.");
        });
});

verificationSubmit.addEventListener("click", function () {
    const enteredCode = parseInt(verificationInput.value.trim(), 10);

    if (enteredCode === verificationCode) {
        verificationCodeBlock.style.display  = 'none'
        verificationSuccess.style.display = 'block'
        // alert("Авторизация успешна!");

        setTimeout(() => {
            phoneModal.style.opacity = "0";
            setTimeout(() => {
                phoneModal.style.visibility = "hidden";
            }, 300);
        }, 2000);

    } else {
        verificationCodeAlert.style.display = 'block'
    }

});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Отменяем стандартную отправку формы
        // Получаем значения полей
        const numberOfVisitsFromStr = form.querySelectorAll("#visits input")[0].value;
        // const numberOfVisitsToStr = parseInt(form.querySelectorAll("#visits input")[1].value, 10) || 0;
        const numberOfVisitsToStr = form.querySelectorAll("#visits input")[1].value;


        const numberOfVisitsFrom = Math.max(1, parseInt(numberOfVisitsFromStr, 10));
        const numberOfVisitsTo = Math.max(1, parseInt(numberOfVisitsToStr, 10));
        const dateVisitFrom = form.querySelectorAll("#date-visit input")[0].value || null;
        const dateVisitTo = form.querySelectorAll("#date-visit input")[1].value || null;
        const timeToStartSending = form.querySelector("input[type='datetime-local']").value || null;

        // // Проверки перед отправкой формы

        if (numberOfVisitsFrom > numberOfVisitsTo) {
            alert("Количество посещений От: должно быть меньше Количество посещений До:");
            return;
        }


        if (dateVisitFrom && dateVisitTo) {
            if (new Date(dateVisitFrom) >= new Date(dateVisitTo)) {
                alert("Дата начала посещения должна быть раньше даты окончания.");
                return;
            }
        }

        if (timeToStartSending) {
            if (new Date(timeToStartSending) <= new Date()) {
                alert("Время начала отправки должно быть в будущем.");
                return;
            }
        }

        // Формируем объект с данными
        const requestData = {
            phone: phoneInput.value.trim(),
            restName: form.querySelector("#name-rest select").value,
            numberOfVisitsFrom,
            numberOfVisitsTo,
            dateVisitFrom,
            dateVisitTo,
            textMessage: form.querySelector("#input-message-text").value.trim(),
            linkImage: form.querySelector("#link-image input").value.trim(),
            textButton: form.querySelectorAll(".button-tg input")[0].value.trim() || null,
            linkButton: form.querySelectorAll(".button-tg input")[1].value.trim() || null,
            timeToStartSending
        };

        console.log("Отправка данных:", requestData);
        //
        // // Формируем объект с данными
        // const requestData = {
        //     phone: phoneInput.value.trim(), // Добавляем телефон пользователя
        //     restName: form.querySelector("#name-rest select").value,
        //     numberOfVisitsFrom: parseInt(form.querySelectorAll("#visits input")[0].value, 10) || null,
        //     numberOfVisitsTo: parseInt(form.querySelectorAll("#visits input")[1].value, 10) || null,
        //     dateVisitFrom: form.querySelectorAll("#date-visit input")[0].value || null,
        //     dateVisitTo: form.querySelectorAll("#date-visit input")[1].value || null,
        //     textMessage: form.querySelector("#input-message-text").value.trim(),
        //     linkImage: form.querySelector("#link-image input").value.trim(),
        //     textButton: form.querySelectorAll(".button-tg input")[0].value.trim() || null,
        //     linkButton: form.querySelectorAll(".button-tg input")[1].value.trim() || null,
        //     timeToStartSending: form.querySelector("input[type='datetime-local']").value || null
        // };
        //
        // console.log("Отправка данных:", requestData);

        try {
            const response = await fetch("https://sending.synergy-api.online/send-sending", {
            // const response = await fetch("http://127.0.0.1:5057/api/send", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`Ошибка: ${response.statusText}`);
            }

            form.reset();
            const result = await response.json();
            console.log("Ответ от сервера:", result);

            // Показать модальное окно успеха
            modal.style.visibility = "visible";
            modal.style.opacity = "1";
        } catch (error) {
            console.error("Ошибка при отправке запроса:", error);
            alert("Ошибка при отправке данных!");
        }
    });

    // Закрытие модального окна успеха
    closeModal.addEventListener("click", function () {
        modal.style.opacity = "0";
        setTimeout(() => {
            modal.style.visibility = "hidden";
        }, 300);
    });

});
