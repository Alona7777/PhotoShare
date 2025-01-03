
# 📸 PhotoShare

**PhotoShare** — це сучасний застосунок для роботи з фотографіями, створений на основі **FastAPI** та **Python**.
   Він дозволяє користувачам завантажувати, переглядати, редагувати та ділитися фото у зручний і швидкий спосіб.
   Ідеальне рішення для персонального використання або обміну фотографіями у спільнотах.

## 🛠 Функціонал

- 📤 **Завантаження фотографій**: швидке та зручне додавання фото.
- 🖼 **Перегляд галереї**: можливість переглядати фото в зручному інтерфейсі.
- ✂️ **Редагування фотографій**: обрізка, зміна розміру, додавання фільтрів.
- 🔗 **Обмін фотографіями**: генеруйте посилання для швидкого доступу до фото.
- 👥 **Підтримка декількох користувачів**: кожен користувач має свій акаунт та персональну галерею.

## 🚀 Встановлення та запуск

1. Клонуйте репозиторій:

    ```bash
    git clone https://github.com/Alona7777/PhotoShare.git
    ```

2. Перейдіть у директорію проєкту:

    ```bash
    cd PhotoShare
    ```

3. Встановіть необхідні залежності:
    - Використовуючи requirements.txt

        ```bash
        pip install -r requirements.txt
        ```

    - Використовуючи Poetry:

        ```bash
        poetry install
        ```
        
        ```bash
        poetry shell
        ```

4. Щоб запустити Redis та PostgreSQL, використовуючи наданий файл docker-compose.yml, виконайте наступну команду у вашому терміналі:

    ```bash
    docker-compose up
    ```

5. Запустіть FastAPI сервер:

    ```bash
    uvicorn main:app --reload
    ```

6. Відкрийте браузер і перейдіть за адресою:

    ```
    http://127.0.0.1:8000
    ```

## 🎨 Інтерфейс користувача

![Скріншот галереї PhotoShare](https://via.placeholder.com/800x400.png?text=Gallery+Screenshot)

*Приклад перегляду фотографій у PhotoShare*

## 🖥 Технології

- **Python** — основна мова програмування застосунку
- **FastAPI** — потужний фреймворк для створення веб-застосунків
- **Jinja2** — для шаблонізації HTML сторінок
- **PostgreSQL** — легка база даних для зберігання користувацьких даних та фотографій
- **HTML/CSS/JavaScript** — для фронтенд частини застосунку

## 📋 API документація

FastAPI автоматично генерує інтерактивну документацію API, яку можна переглянути за адресою:

```
http://127.0.0.1:8000/docs
```

Там ви зможете тестувати та переглядати всі доступні API-ендпоінти для роботи з фото.

## 📦 Вимоги

- **Python** 3.8 або новіший
- **FastAPI** та інші залежності, зазначені у файлі `requirements.txt`
- **Uvicorn** для запуску серверу

## 👩‍💻 Автори

- **Команда: "Team-1"** 
                   Team Lead: Альона Боголєпова,
                   Scrum: Ігор Рись,
                   Developers: Артем Набока,
                               Володимир Пругло,
                               Олена Маляренко.


## 📜 Ліцензія

Цей проєкт ліцензований відповідно до [MIT License](LICENSE).

## 📧 Контакти

Якщо у вас виникли питання або пропозиції щодо покращення проєкту, не соромтесь зв'язатися зі мною через GitHub.
