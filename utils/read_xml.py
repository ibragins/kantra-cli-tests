import os
from utils import constants
from lxml import etree


def manage_credentials_in_maven(path, reset=False):
    tree = etree.parse(path)
    root = tree.getroot()

    namespaces = {'mvn': 'http://maven.apache.org/SETTINGS/1.2.0'}

    if not reset:
        username = os.getenv(constants.GIT_USERNAME)
        password = os.getenv(constants.GIT_PASSWORD)
    else:
        username = ''
        password = ''

    for server in root.xpath('//mvn:server', namespaces=namespaces):
        username_elem = server.find('mvn:username', namespaces)
        password_elem = server.find('mvn:password', namespaces)

        if username_elem is not None:
            username_elem.text = username
        if password_elem is not None:
            password_elem.text = password

    tree.write(path, pretty_print=True, xml_declaration=True, encoding='UTF-8')

