# 🚀 JedanCodeAcadamyRGBackend: Django Registration App

<p align="center">
  <a href="https://github.com/Jedan-Technology/JedanCodeAcadamyRGBackend">
    <img alt="Github" src="https://img.shields.io/github/workflow/status/Jedan-Technology/JedanCodeAcadamyRGBackend/Test?label=Test&logo=github&color=blueviolet"/>
  </a>
  <a href="LICENSE">
    <img alt="License" src="https://img.shields.io/static/v1?logo=GPL&color=Blue&message=GPL-v3&label=License"/>
  </a>
  <a href="https://pypi.org/project/smartbetsAPI">
    <img alt="PyPi" src="https://img.shields.io/static/v1?logo=pypi&label=Pypi&message=v1.1.4&color=green"/>
  </a>

  <a href="#">
    <img alt="Passing" src="https://img.shields.io/static/v1?logo=Docs&label=Docs&message=Passing&color=green"/>
  </a>
  <a href="#">
    <img alt="Coverage" src="https://img.shields.io/static/v1?logo=Coverage&label=Coverage&message=85%&color=yellowgreen"/>
  </a>
  
  <a href="https://pepy.tech/project/smartbetsapi"></a>
</p>


## 📚 Overview

Welcome to the JedanCodeAcadamyRGBackend Django Registration App! This robust application handles user registration functionalities for both web and Telegram bot interfaces. Empowering users to effortlessly sign up, log in, and manage their accounts seamlessly.

## ✨ Features

- 🤝 User Registration
- 🔐 User Authentication
- 🌐 Web Interface
- 🤖 Telegram Bot Interface

## 📋 Table of Contents

1. [Getting Started](#-getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Configuration](#configuration)
2. [Usage](#-usage)
   - [Web Interface](#web-interface)
   - [Telegram Bot](#telegram-bot)
3. [API Reference](#-api-reference)
   - [Endpoints](#endpoints)
   - [Telegram Bot Commands](#telegram-bot-commands)
4. [Contributing](#-contributing)
5. [License](#-license)

## 🚀 Getting Started

### Prerequisites

- 🐍 Python (version 3.10)
- 🌐 Django (version 5.1)
- 🤖 Telegram Bot Token (Create a bot on Telegram and obtain the token)

## ER Diagram
![ER Diagram](https://github.com/Jedan-Technology/JedanCodeAcadamyRGBackend/blob/main/Assets/ErDiagram.png)


### 🛠 Installation

### 🛠 Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/Jedan-Technology/JedanCodeAcadamyRGBackend.git
   ```
2. Install dependencies:

```
pip install -r requirements.txt
```
3. ⚙️ Configuration
Configure Django settings:

```
cp .env.example .env
```
Update the .env file with your configuration details.

4. Migrate the database:

```
python manage.py migrate
```
## 🚀 Usage
- Web Interface
Run the development server:

```
python manage.py runserver
```
Access the web interface at http://127.0.0.1:8000 in your browser.

- Telegram Bot
Deploy your Django app with webhook support.

Set the Telegram bot webhook:

```
python manage.py set_webhook <your-telegram-bot-token>
```
Interact with the bot on Telegram using the registered commands.

## 📚 API Reference
Endpoints
- POST /api/register/: Register a new user.
- POST /api/login/: Log in and obtain an authentication token.
- POST /api/logout/: Log out and invalidate the authentication token.
...
# 🤖 Telegram Bot Commands
- /start: Start the registration process.
- /register: Register a new user through the Telegram bot.
- /login: Log in through the Telegram bot.
...
## 🤝 Contributing
Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests to us.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
