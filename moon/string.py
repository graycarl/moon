# -*- coding: utf-8 -*-
__all__ = ["truncate_unicode", "ISBNError", "validate_isbn"]


# Truncate String
###############################################################################
def truncate_unicode(s, length=50, ucas=2, end="..."):
    """ 把unicode字符串切断显示，非ascii字符算两个长度 """
    assert isinstance(s, unicode)
    if len(s) * 2 < length:
        return s
    curl = 0
    cs = []
    for c in s:
        if c > u'\u00ff':
            curl += ucas
        else:
            curl += 1
        if curl > length:
            break
        cs.append(c)
    return "".join(cs) + end


# Validate ISBN
###############################################################################
class ISBNError(Exception):
    pass


def validate_isbn(raw_isbn, allow_dash=False):
    isbn = raw_isbn.replace("-", "").upper()
    if (len(isbn) != len(raw_isbn)) and (not allow_dash):
        raise ISBNError("there are dashes in isbn")

    def isbn10(isbn):
        s = 0
        for i in range(0, 9):
            s += int(isbn[i]) * (10-i)
        n = 11 - (s % 11)
        n = "0" if n == 11 else "X" if n == 10 else str(n)
        return n == isbn[9]

    def isbn13(isbn):
        s = 0
        for i in range(0, 12, 2):
            s += int(isbn[i])
            s += int(isbn[i+1]) * 3
        n = 10 - (s % 10)
        n = "0" if n == 10 else str(n)
        return n == isbn[12]

    length = len(isbn)
    try:
        if length == 10:
            if not isbn10(isbn):
                raise ISBNError("isbn validate error")
        elif length == 13:
            if not isbn13(isbn):
                raise ISBNError("isbn validate error")
        else:
            raise Exception
    except ISBNError:
        raise
    except:
        raise ISBNError("isbn format error")

    return isbn
