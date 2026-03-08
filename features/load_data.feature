Feature: Загрузка данных из JSON
  As a пользователь системы планирования
  I want загружать данные о группах, преподавателях и занятиях
  So that можно строить расписание

  Background:
    Given система инициализирована
    And существуют тестовые JSON файлы

  Scenario: Успешная загрузка всех типов данных
    When пользователь загружает файл "data/test.json"
    Then данные успешно загружены
      And загружены группы
      And загружены преподаватели
      And загружены аудитории
      And загружены предметы
      And загружены занятия

  Scenario Outline: Обработка ошибок при загрузке
    When пользователь пытается загрузить "<file>"
    Then возникает ошибка "<error>"

    Examples:
      | file | error |
      | nonexistent.json | не найден |
      | data/invalid.json | формата |
      | data/missing_fields.json | missing field |