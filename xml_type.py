from abc import ABCMeta, abstractmethod
from base64 import b64encode
from typing import Any
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, tostring


class XmlType:
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def tag(self):
        pass

    @staticmethod
    def __append_if_xml_element(e: Element, c: Any):
        if isinstance(c, XmlType):
            e.append(c.to_xml())

    def to_xml(self) -> Element:
        e = Element(self.tag)

        for child in self.__dict__.values():
            XmlType.__append_if_xml_element(e, child)
            if isinstance(child, list):
                for c in child:
                    XmlType.__append_if_xml_element(e, c)

        return e


class ComplexType(XmlType):

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    def __init__(self, **params):
        self._tag = "undefined"
        for i, (k, v) in enumerate(params.items()):
            self.__insert(i, k, v)

    def __insert(self, i: int, k: str, v: Any):
        """
        Insert a XmlElement into this instance.

        i: item position at which to insert
        k: name of the element
        v: text value of the element
        """
        if isinstance(v, str):
            e = StringType(k, v)
        elif isinstance(v, int):
            e = StringType(k, str(v))
        elif isinstance(v, bytes):
            e = BytesType(k, v)
        elif v is None:
            return
        elif isinstance(v, ComplexType):
            e = v
            v.tag = k
        elif isinstance(v, XmlType):
            e = v
        elif isinstance(v, list):
            e = v
            for _v in v:
                if isinstance(_v, ComplexType):
                    _v.tag = k
        else:  # Other types not supported yet
            raise UnsupportedElementException(f"Element: {v} of type {type(v)} is not supported yet.")

        item_str = f"item{i}"
        self.__dict__[item_str] = e


class RootType(ComplexType):

    def __init__(self, tag, schema_location, **params):
        super().__init__(**params)

        self.tag = tag
        self.schema_location = schema_location

        for k, v in params.items():
            if isinstance(v, ComplexType):
                v.tag = k
            if isinstance(v, list):
                for _v in v:
                    if isinstance(_v, ComplexType):
                        _v.tag = k

    def to_xml(self) -> Element:
        e = super().to_xml()
        e.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        e.set('xsi:noNamespaceSchemaLocation', self.schema_location)
        return e

    def __reparsed(self):
        rough_string = tostring(self.to_xml(), 'utf-8')
        return parseString(rough_string)

    def __str__(self):
        return self.__reparsed().toprettyxml(indent="    ")

    def write_to_file(self, path: str):
        tree = self.__reparsed().toprettyxml(indent="    ", encoding='UTF-8')
        with open(path, 'wb') as f:
            f.write(tree)


class StringType(XmlType):

    @property
    def tag(self) -> str:
        return self._tag

    def __init__(self, tag: str, text: str):
        self._tag = tag
        self.text = text

    def to_xml(self) -> Element:
        e = Element(self.tag)
        e.text = self.text
        return e


class BytesType(XmlType):

    @property
    def tag(self) -> str:
        return self._tag

    def __init__(self, tag: str, value: bytes):
        self._tag = tag
        self.text = b64encode(value).decode('ascii')

    def to_xml(self) -> Element:
        e = Element(self.tag)
        e.text = self.text
        return e


class UnsupportedElementException(Exception):
    pass
