# -*- coding: utf-8 –*-


def force_str(text, encoding="utf-8", errors='strict'):
    """ 转换成string
    """
    t_type = type(text)
    if t_type == str:
        return text
    elif t_type == unicode:
        return text.encode(encoding, errors)
    return str(text)


def force_unicode(text, encoding="utf-8", errors='strict'):
    """ 转换成 unicode
    """
    t_type = type(text)
    if t_type == unicode:
        return text

    elif t_type == str:
        return text.decode(encoding, errors)
    elif hasattr(text, '__unicode__'):
        return unicode(text)

    return unicode(str(text), encoding, errors)