# 💼 Caçador de Vagas Pro - Telegram Bot

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

Um bot de Telegram focado em otimizar a busca por empregos. Ele atua como um agregador de vagas, vasculhando múltiplos sites de emprego no Brasil simultaneamente e entregando as melhores oportunidades diretamente no chat do usuário, com sistema de cache e filtro de precisão.

## ✨ Funcionalidades

* **Busca Multi-Sites:** Vasculha plataformas como Vagas.com, Indeed, InfoJobs, Catho, Trabalha Brasil, entre outras.
* **Filtro Sniper:** Filtra resultados falsos-positivos ou "vagas recomendadas" dos sites, garantindo que a palavra-chave do cargo exigido esteja no título da vaga.
* **Sistema de Cache (SQLite):** Armazena as últimas buscas por 30 minutos em um banco de dados local. Se o usuário repetir a busca, a resposta é instantânea, economizando banda e evitando bloqueios por requisições em excesso.
* **Geolocalização Automática:** Utiliza a API `ipapi` para sugerir a localização atual do usuário baseada no IP, facilitando a busca regional.
* **Banners Visuais:** Gera dinamicamente tags visuais (via Shields.io) indicando a fonte de origem da vaga no chat do Telegram.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Integração:** `pyTelegramBotAPI` (Comunicação com a API do Telegram)
* **Web Scraping:** `BeautifulSoup4` e `requests`
* **Banco de Dados:** `SQLite3` (Nativo do Python)

## 🚀 Como rodar o projeto localmente

1. Clone este repositório para a sua máquina:
```bash
git clone [https://github.com/kctxdev/cacador-de-vagas-bot.git](https://github.com/kctxdev/cacador-de-vagas-bot.git)
