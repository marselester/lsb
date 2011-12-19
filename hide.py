#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Автономный «скрыватель».

Помещает произвольно выбранный файл в заданное BMP изображение.
"""
import sys
marker = 'iddqd'


class HideException(Exception):
    """Базовый класс для ошибок в модуле «скрыватель»."""
    pass


class UsageException(HideException):
    """Класс для ошибок использования утилиты."""

    def __str__(self):
        return self.message + '\nUsage: hide.py [bmp image] [any file]'


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


def hide(bmp_filename, src_filename):
    """Помещает в BMP изображение любой файл, включая его название.

    У пикселей (байтов) в изображении меняет младшие биты на те,
    что содержатся в потоке бит скрываемого файла.
    Для определения в BMP секретных данных ставятся метки.
    """
    src = open(src_filename, 'rb')
    secret = marker + src_filename + marker + src.read() + marker
    src.close()

    bmp = open(bmp_filename, 'rb+')
    bmp.seek(55)
    container = bmp.read()

    need = 8 * len(secret) - len(container)
    if need > 0:
        raise HideException('BMP size is not sufficient for confidential file.'
                            '\nNeed another %s byte.' % need)
    cbits = byte2bin(container)
    encrypted = []
    for sbits in byte2bin(secret):
        for bit in sbits:
            bits = cbits.next()
            # Замена младшего бита в контейнерном байте
            bits = bits[:-1] + bit
            b = chr(int(bits, 2))
            # Замена байта в контейнере
            encrypted.append(b)

    bmp.seek(55)
    bmp.write(''.join(encrypted))
    bmp.close()


def main(argv=None):
    """Запускает процесс скрывания.

    Обрабатывает исключения при сокрытии файла. Отображает справку
    по использованию утилиты."""
    if argv is None:
        argv = sys.argv
    try:
        if len(argv) != 3:
            raise UsageException('You need specify a BMP and the file '
                                 'you want to hide.')
        hide(argv[1], argv[2])
    except (IOError, HideException), err:
        print >> sys.stderr, err
        return 2

if __name__ == '__main__':
    sys.exit(main())
