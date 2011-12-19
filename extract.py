#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Автономный «экстрактор».

Определяет, что в заданном изображении есть файл, положенный туда «скрывателем»
и полностью его восстанавливает (включая имя).
"""
import sys
marker = 'iddqd'


class ExtractException(Exception):
    """Базовый класс для ошибок в модуле «экстрактор»."""
    pass


class UsageException(ExtractException):
    """Класс для ошибок использования утилиты."""

    def __str__(self):
        return self.message + '\nUsage: extract.py [bmp image]'


def bin(s):
    """Переводит число в двоичную систему счисления.

    Результат в виде битовой строки.
    """
    return str(s) if s <= 1 else bin(s >> 1) + str(s & 1)


def byte2bin(bytes):
    """Поставляет байты в виде битовых строк.

    Преобразует символ в число.
    Переводит число в двоичную систему с дополнением нулей.
    """
    for b in bytes:
        yield bin(ord(b)).zfill(8)


def decrypt_char(container):
    """Поставляет расшифрованные символы.

    Извлекает из 8 байт младшие биты, формирует из них битовую строку.
    Переводит из двоичной системы в десятичную.
    Преобразует число в символ.
    """
    sbits = ''
    for cbits in byte2bin(container):
        sbits += cbits[-1]
        if len(sbits) == 8:
            yield chr(int(sbits, 2))
            sbits = ''


def extract(bmp_filename):
    """Извлекает из BMP скрытый файл, включая его название."""
    bmp = open(bmp_filename, 'rb')
    bmp.seek(55)
    container = bmp.read()
    bmp.close()

    decrypted = []
    for b in decrypt_char(container):
        decrypted.append(b)
        # Определение, что в заданном изображении есть файл
        if (len(marker) == len(decrypted) and
            marker != ''.join(decrypted)):
            raise ExtractException('The image does not contain '
                                   'confidential file.')
    if len(decrypted) > len(marker):
        # Список ['', 'source file name', 'source file data', '']
        decrypted = ''.join(decrypted).split(marker)
        src_filename = decrypted[1]
        src_data = decrypted[2]
        src = open(src_filename, 'wb')
        src.write(src_data)
        src.close()


def main(argv=None):
    """Запускает процесс извлечения.

    Обрабатывает исключения при извлечении файла. Отображает справку
    по использованию утилиты."""
    if argv is None:
        argv = sys.argv
    try:
        if len(argv) != 2:
            raise UsageException('You need specify a BMP.')
        extract(argv[1])
    except (IOError, ExtractException), err:
        print >> sys.stderr, err
        return 2

if __name__ == '__main__':
    sys.exit(main())
