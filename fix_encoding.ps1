# Исправляем кодировку в main.py
$filePath = "app\main.py"
$content = Get-Content $filePath -Raw -Encoding UTF8
# Заменяем испорченную кириллицу на правильную
$content = $content -replace "������-����������", "AI-разработка"
$content = $content -replace "�������� � ����������� �������� ��� ������, �����������, �����, �����", "Интеграция с языковыми моделями для чатов, ассистентов, ботов, игр"
$content = $content -replace "���������� ����������� ������ ��� ��-�����������", "Создание умных агентов для веб-приложений"
$content = $content -replace "���������� � ChatGPT, Claude, Gemini, YandexGPT � ��.", "Взаимодействие с ChatGPT, Claude, Gemini, YandexGPT и др."
$content = $content -replace "���������� ��-�������", "Разработка веб-приложений"
$content = $content -replace "��-���������� � ���-����", "Веб-приложения с ИИ-функциями"
# Сохраняем исправленный файл
$content | Out-File $filePath -Encoding UTF8
Write-Host "✅ Файл main.py исправлен"
