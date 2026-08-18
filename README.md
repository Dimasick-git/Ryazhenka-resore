# Ryazhenka-resore

**Ryazhenka-resore** — публичное зеркало отдельных ресурсов из release `Homebrews` проекта [Ultra-NX/Ultra-Resources](https://github.com/Ultra-NX/Ultra-Resources). Оно создано для устойчивых ссылок в **Ryazhenkabestcfw Tuner** и не является независимым источником сборок.

> Все синхронизируемые файлы сохраняют исходные имена. В `resources.json` для каждого asset записываются исходная ссылка, дата исходного release, размер и SHA-256 полученной копии.

## Автоматическая синхронизация

Workflow запускается вручную и по расписанию каждые шесть часов. Он получает release `Homebrews` upstream-проекта, сверяет контрольные суммы выбранных файлов, обновляет `resources.json` только при реальном изменении и перезаписывает asset с тем же именем в единственном release зеркала.

| Asset | Назначение в Ryazhenkabestcfw Tuner |
|---|---|
| `DBI.RU.zip` | Установка DBI |
| `linkalho.zip` | Установка Linkalho |
| `MicroMemBench.zip` | Проверка памяти |
| `MasterVolume.zip` | Базовый пакет MasterVolume |
| `DuckStation.zip` | Эмулятор PlayStation 1 |
| `Benchmark-Toolbox.zip` | Диагностика производительности |
| `MemToolkitNX.zip` | Диагностика памяти |
| `MemToolkitNX-OLD.zip` | Старая версия диагностики памяти |

## Правила использования

Зеркало предназначено только для загрузки данных из тюнера. При обновлении исходного ресурса workflow не изменяет его содержимое: он копирует файл, фиксирует проверочную сумму и сохраняет ссылку на upstream.

Исходный репозиторий не содержит указанной лицензии. Репозиторий-зеркало сохраняет атрибуцию и ссылки на источник, а перечень файлов ограничен компонентами, выбранными для Ryazhenkabestcfw Tuner.

## Связанные проекты

- [Ultra-NX/Ultra-Resources](https://github.com/Ultra-NX/Ultra-Resources) — исходник ресурсов.
- [Ryazhenkabestcfw Tuner](https://github.com/Dimasick-git/Ryazhenkabestcfw-Tuner) — потребитель стабильных ссылок зеркала.
