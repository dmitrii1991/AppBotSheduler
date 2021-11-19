[![Python version](https://img.shields.io/badge/Python-3.8.+-green)](https://www.python.org/)
[![GitHub issues][issues-shield]][issues-url]
![GitHub repo size](https://img.shields.io/github/languages/code-size/dmitrii1991/AppBotSheduler)
![GitHub last commit](https://img.shields.io/github/last-commit/dmitrii1991/AppBotSheduler)
[![GitHub stars][stars-shield]][stars-url]

# Bot project, API integration and task execution worker

Проект Бота, интеграции с API и воркера исполнения задач


## Customization
Переименовать и настроить 2 файла
- settings_test.py в settings_test.py
- env_test.py в env_test.py 


## Infrastructure

- Redis (NoSQL)
- PostgreSql (SQL)


##  Run
```shell script
docker-compose --env-file .env up
```

## API documentation
* http://127.0.0.1:80/docs
* http://127.0.0.1:80/redoc

## For the future

* encryption


[stars-shield]: https://img.shields.io/github/stars/dmitrii1991/AppBotSheduler?style=social
[stars-url]: https://github.com/dmitrii1991/AppBotSheduler/stargazers

[issues-shield]: https://img.shields.io/github/issues/dmitrii1991/AppBotSheduler
[issues-url]: https://github.com/dmitrii1991/AppBotSheduler/issues
