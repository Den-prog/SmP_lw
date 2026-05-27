import os
import re
import datetime
import xml.sax
from xml.dom import minidom

#SAX ПАРСЕР (Завдання 1, 2, 3)

class EcoSaxHandler(xml.sax.ContentHandler):
    """
    Завдання 1: Клас-обробник початкових і кінцевих тегів, 
    а також текстового вмісту (аналог функцій обробників у PHP).
    """
    def __init__(self):
        super().__init__()
        self.current_tag = ""
        self.current_data = ""
        self.current_item = {}
        self.items_list = []

    #обробник початкових тегів
    def startElement(self, tag, attributes): # type: ignore
        self.current_tag = tag
        if tag == "initiative":
            self.current_item = {"id": attributes.get("id", "")}

    #обробник текстового вмісту тегів
    def characters(self, content):
        self.current_data += content.strip()

    #обробник закриваючих (кінцевих) тегів
    def endElement(self, tag): # type: ignore
        if tag == "title":
            self.current_item["title"] = self.current_data
        elif tag == "location":
            self.current_item["location"] = self.current_data
        elif tag == "points":
            self.current_item["points"] = self.current_data
        elif tag == "initiative":
            self.items_list.append(self.current_item)
        
        #очищуємо буфер накопичення тексту
        self.current_data = ""


def parse_eco_initiatives_sax(xml_string):
    """
    Завдання 1-2: Створення парсера, реєстрація обробників подій 
    та запуск процесу аналізу документа.
    """
    #створення об'єкта парсера
    parser = xml.sax.make_parser()
    
    #створення та реєстрація обробника вмісту
    handler = EcoSaxHandler()
    parser.setContentHandler(handler) # type: ignore
    
    #запуск парсингу рядка з XML-структурою
    xml.sax.parseString(xml_string.encode('utf-8'), handler)
    return handler.items_list



#Завдання 4


def get_or_create_guestbook(file_path='guestbook.xml'):
    """
    Завдання 4: Створення об'єкта DOM, перевірка існування файлу.
    Якщо існує — завантаження та отримання кореневого елемента,
    якщо ні — створення нового кореня <users>.
    """
    if os.path.exists(file_path):
        #завантажуємо існуючий XML-документ в об'єкт DOM
        dom = minidom.parse(file_path)
        root = dom.documentElement
    else:
        #створюємо новий об'єкт DOM та кореневий елемент «users»
        dom = minidom.getDOMImplementation().createDocument(None, "users", None)
        root = dom.documentElement
        
        #одразу зберігаємо базову структуру в файл
        with open(file_path, "w", encoding="utf-8") as f:
            dom.writexml(f, indent="", addindent="  ", newl="\n", encoding="utf-8")
            
    return dom, root


def add_guestbook_entry(username, message, file_path='guestbook.xml'):
    """Додавання нового елемента в дерево DOM та збереження на диск."""
    dom, root = get_or_create_guestbook(file_path)
    
    #очищуємо порожні текстові вузли від попереднього форматування minidom
    for node in list(root.childNodes): # type: ignore
        if node.nodeType == node.TEXT_NODE and not node.nodeValue.strip():
            root.removeChild(node)# type: ignore
            
    #створення структури нового запису
    user_elem = dom.createElement("user")
    
    name_elem = dom.createElement("name")
    name_elem.appendChild(dom.createTextNode(username))
    
    msg_elem = dom.createElement("message")
    msg_elem.appendChild(dom.createTextNode(message))
    
    date_elem = dom.createElement("date")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    date_elem.appendChild(dom.createTextNode(now_str))
    
    #прив'язуємо піделементи до батьківського вузла
    user_elem.appendChild(name_elem)
    user_elem.appendChild(msg_elem)
    user_elem.appendChild(date_elem)
    
    #додаємо елемент користувача до кореневого елемента <users>
    root.appendChild(user_elem)# type: ignore
    
    #запобігаємо розмноженню порожніх рядків у файлі через специфіку minidom
    clean_xml = re.sub(r'>\s+<', '><', dom.toxml())
    dom_clean = minidom.parseString(clean_xml)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(dom_clean.toprettyxml(indent="  "))


def read_guestbook_entries(file_path='guestbook.xml'):
    """Читання записів з об'єкта DOM для рендерингу на сторінці."""
    if not os.path.exists(file_path):
        return []
        
    dom = minidom.parse(file_path)
    users = dom.getElementsByTagName("user")
    entries = []
    
    for user in users:
        name = user.getElementsByTagName("name")[0].firstChild.nodeValue if user.getElementsByTagName("name") else "Анонім" # type: ignore
        msg = user.getElementsByTagName("message")[0].firstChild.nodeValue if user.getElementsByTagName("message") else "" # type: ignore
        date = user.getElementsByTagName("date")[0].firstChild.nodeValue if user.getElementsByTagName("date") else "" # type: ignore
        entries.append({"name": name, "message": msg, "date": date})
        
    return entries