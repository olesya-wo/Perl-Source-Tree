# Perl SourceTree
Плагин для SublimeText3, строящий YAML-структуру дерева классов и их методов всех Perl-модулей в текущей открытой папке.

## Установка
- Скопировать `PerlSourceTree.py` в папку с плагинами SublimeText3.<br/>(В Windows10 это `C:\Users\Username\AppData\Roaming\Sublime Text 3\Packages\User`. В linux `/home/Username/.config/sublime-text-3/Packages/User`)
- Preferences > Key Bindings > `{ "keys": ["ctrl+shift+c"], "command": "perl_source_tree" }`<br/>Или в консоли (Ctrl+\`) view.run_command('perl_source_tree') для разового запуска
