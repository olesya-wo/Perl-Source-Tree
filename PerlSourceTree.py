# https://github.com/olesya-wo/Perl-Source-Tree
import sublime
import sublime_plugin
import os
import re


class TreeNode:
    name = ''
    children = None
    functions = None

    def __init__(self, name: str):
        self.name = name
        self.children = dict()

    # Рекурсивная функция для заполнения дерева
    def insert_child_to_tree(self, module: str, subs: [str]) -> None:
        parts = module.split('::')
        if not parts:
            return
        item = parts.pop(0)
        if parts:
            if not self.children.get(item):
                self.children[item] = TreeNode(item)
            self.children[item].insert_child_to_tree('::'.join(parts), subs)
        else:
            self.children[item] = TreeNode(item)
            self.children[item].functions = subs


class Folder:
    path = ''  # /абсолютный/путь/папки/проекта/
    root_node = None  # Корневой элемент дерева с именем в виде директории
    modules = None  # Словарь массивов имён модулей. Ключ - имя модуля

    def __init__(self, path: str):
        self.path = path
        self.modules = dict()

    # Обход всех файлов
    def process(self) -> None:
        file_pattern = re.compile(".+\.pm$", re.IGNORECASE)
        for root, dirs, files in os.walk(self.path):
            for name in files:
                if not file_pattern.match(name):
                    continue
                fn = os.path.join(root, name)
                self.process_file(fn)

    # Заполнение словаря modules
    def process_file(self, filename: str) -> None:
        package_pattern = re.compile("^\s*package\s+([\w:]+);")
        sub_pattern = re.compile("^\s*sub\s+(\w+)[\s{$]")
        with open(filename) as file:
            module = None
            for cnt, line in enumerate(file):
                res = re.search(package_pattern, line)
                if res:
                    module = res.group(1)
                    self.modules[module] = []
                if not module:
                    continue
                res = re.search(sub_pattern, line)
                if res:
                    sub = res.group(1)
                    self.modules[module].append(sub)


class PerlSourceTreeCommand(sublime_plugin.TextCommand):
    tree_view = None
    edit_object = None
    folders_list = []
    indent = '  '

    def run(self, edit):
        # Чистим от старых данных
        self.folders_list.clear()
        # Сохранение глобально объекта модификации
        self.edit_object = edit
        # Получаем список папок и собираем по каждой список модулей с массивом функций
        folders = self.view.window().folders()
        for folder in folders:
            path = Folder(folder)
            path.process()
            if path.modules:
                self.folders_list.append(path)
        # Если никаких модулей не найдено, выводим сообщение и выходим
        if not self.folders_list:
            message = 'No perl modules found'
            self.view.window().status_message(message)
            self.view.show_popup(message)
            return
        # Строим по найденным модулям дерево
        for path in self.folders_list:
            path.root_node = TreeNode(path.path)
            for module in path.modules.keys():
                path.root_node.insert_child_to_tree(module, path.modules[module])
        # Открываем новую вкладку и сохраняем ссылку на неё
        self.tree_view = self.view.window().new_file()
        # Строим по дереву YAML-структуру
        for path in self.folders_list:
            self.print_tree(path.root_node, 0)
        # Некоторые настройки вкладки
        self.tree_view.set_read_only(True)
        self.tree_view.set_scratch(True)
        self.tree_view.set_syntax_file('YAML.sublime-syntax')
        self.tree_view.set_name('Perl SourceTree')

    # Рекурсивная функция построения YAML-структуры по дереву tree
    def print_tree(self, elem: TreeNode, indent_level: int) -> None:
        indent_str = self.indent * indent_level
        self.append_line(indent_str + '- ' + elem.name + ':')
        if elem.functions:
            for fn in sorted(elem.functions):
                self.append_line(indent_str + self.indent + '- ' + fn + '()')
        if elem.children:
            for ch in sorted(elem.children.keys()):
                self.print_tree(elem.children[ch], indent_level + 1)

    # Макрос для добавление строки в конец view
    def append_line(self, string: str) -> None:
        pos = self.tree_view.sel()[0].begin()
        self.tree_view.insert(self.edit_object, pos, string + "\n")
