# -*- coding: utf-8 –*-

import re
from lib.utils.encoding import force_unicode, force_str
from lib.utils.string_operation import is_float, is_int
from lib.utils import add_dict_list, add_dict


space = ['', None, 0.0, 0, ' ', '  ']


class ListCompiles(dict):
    def __missing__(self, key):
        if not isinstance(key, int) or key <= 0:
            return

        add = ', *(\d+\.*\d*)' * (key - 1)
        pattern = '\[([-]*\d+\.*\d*)%s\]' % add
        pattern_obj = re.compile(pattern)
        self[key] = pattern_obj
        return pattern_obj


list_compiles = ListCompiles()


mix_list_compile = re.compile('(\[)([^\[\]]*)(\])')


def force_mix(value):
    """ 支持int, float

    :param value:
    :return:
    """
    if isinstance(value, (int, float)):
        value = str(value)
    if is_int(value):
        return int(value)
    elif is_float(value):
        zero_index = value.index('.')
        f_num = value[zero_index+1:]
        if f_num and int(f_num) > 0:
            return float(value)
        else:
            return int(float(value))
    else:
        return int(value)


def force_mix_str(value):
    """ 支持str、int、float

    :param value:
    :return:
    """
    if is_int(value):
        return int(value)
    elif is_float(value):
        return float(value)
    else:
        return force_to_str(value)


def force_mix_unicode(value):
    """ 支持unicode、int、float

    :param value:
    :return:
    """
    if is_int(value):
        return int(value)
    elif is_float(value):
        return float(value)
    else:
        return force_unicode(value)


def force_list(count):
    """ 强制转换 '[10,10,1],[10,10,10]' -> [[10, 10, 1],[10, 10, 10]]

    :param count: 个数
    :return:
    """
    list_compile = list_compiles[count]

    def decorator(value):
        """

        :param value: [10, 10, 1],[10, 10, 10] 元素只支持int
        :return:
        """
        data = []

        if value in space:
            return data

        for v in list_compile.findall(value):
            data_list = []
            for num in v:
                if is_float(num):
                    data_list.append(float(num))
                else:
                    data_list.append(int(num))
            if data_list:
                data.append(data_list)

        return data

    return decorator


def force_2int_list(value):
    """[1],[1,2] -> [[1], [1,2]]"""

    data = []
    if value in space:
        return data

    if value == 'NA':
        return value

    len = value.count('],[') + 1
    index = 0
    for i in xrange(len):

        start_index = value.find('[', index)
        end_index = value.find(']', index)
        num = value.count(',', start_index, end_index) + 1
        list_compile = list_compiles[num]
        data1 = []
        for v in list_compile.findall(value[start_index: end_index+1]):
            data1.append(map(int, v))
        data.extend(data1)
        index = end_index + 1

    return data


def force_int_list_or_int(value):
    """ 1,2 -> [1, 2]  1 -> 1 '' -> [] '[10,10,10],[10,10,10]' -> [[10,10,10],[10,10,10]]

    :param value:
    :return:
    """
    if value in space:
        return []
    if value == 'NA':
        return value
    if not isinstance(value, basestring):
        return int(value)
    start_index = value.find('[')
    if start_index < 0:
        return [int(i.strip()) for i in value.split(',') if i]
    end_index = value.find(']')
    num = value.count(',', start_index, end_index) + 1
    list_compile = list_compiles[num]
    data = []
    for v in list_compile.findall(value):
        data.append(map(int, v))
    return data


def force_int_list_or_int2(value):
    """ 1,2 -> [1, 2]  1 -> 1 '' -> 0 '[10,10,10],[10,10,10]' -> [[10,10,10],[10,10,10]]

    :param value:
    :return:
    """
    if value in space:
        return 0
    if value == 'NA':
        return value
    if not isinstance(value, basestring):
        return int(value)
    start_index = value.find('[')
    if start_index < 0:
        if ',' not in value:
            return int(value)
        return [int(i.strip()) for i in value.split(',') if i]
    end_index = value.find(']')
    num = value.count(',', start_index, end_index) + 1
    list_compile = list_compiles[num]
    data = []
    for v in list_compile.findall(value):
        data.append(map(int, v))
    return data


def force_int_float_list_or_int_float(value):
    """ 1,2 -> [1, 2]  1 -> 1 '' -> [] '[10,10,10],[10,10,10]' -> [[10,10,10],[10,10,10]]

    :param value:
    :return:
    """
    if value in space:
        return []
    if value == 'NA':
        return value
    if not isinstance(value, basestring):
        return force_mix(value)
    start_index = value.find('[')
    if start_index < 0:
        return [force_mix(i.strip()) for i in value.split(',') if i]
    end_index = value.find(']')
    num = value.count(',', start_index, end_index) + 1
    list_compile = list_compiles[num]
    data = []
    for v in list_compile.findall(value):
        data.append(map(force_mix, v))
    return data


def force_int_list(x):
    try:
        x = str(int(x))
    except ValueError:
        x = x
    except TypeError:
        x = x
    return eval("""[%s]""" % x if x not in [None, '[]', '0', '0.0', 0, 0.0] else"""[]""")


def force_int_or_float_list(value):
    if value in space:
        return []
    if not isinstance(value, basestring):
        return [force_mix(value)]
    return [force_mix(i.strip()) for i in value.split(',') if i]


def force_mix_str_list(value):
    return [force_mix_str(i.strip()) for i in value.split(',') if i] if value not in space else []


def force_mix_unicode_list(value):
    return [force_mix_unicode(i.strip()) for i in value.split(',') if i] if value not in space else []


def force_mix_list_str_list(value):
    data = []

    if value in space:
        return data

    for v in mix_list_compile.findall(value):
        data.append(force_mix_str_list(v[1]))

    return data


def force_mix_list_unicode_list(value):
    data = []

    if value in space:
        return data

    for v in mix_list_compile.findall(value):
        data.append(force_mix_unicode_list(v[1]))

    return data


def force_list_int_list(value):
    data = []

    if value in space:
        return data

    for v in mix_list_compile.findall(value):
        data.append(force_int_list(v[1]))
    return data


def force_mult_dict(start=1):

    def decorator(value):
        data = {}

        if value in space:
            return data

        if isinstance(value, basestring):
            value = eval(value)

        for k, v in enumerate(value, start=start):
            data[k] = v

        return data

    return decorator


def force_mult_list(value):
    data = []

    if value in space:
        return data

    for v in value:
        if v:
            data.append(v)

    return data


def force_mult_list1(value):
    data = []

    if value in space:
        return data

    for v in value:
        data.append(v)

    return data


def force_mult_force_num_list(value):
    data = []

    if value in space:
        return data

    for v in value:
        data.append(v)

    return data


def force_mult_key_dict(value):
    data = {}

    if value in space:
        return data

    for k, v in value:
        data[k] = v

    return data


def force_list_2_to_dict(value):
    """ [1,2,3,4,5,6,7,8] -> {1:2, 3:4, 5:6, 7:8}

    :param value:
    :return:
    """
    data = {}

    if value in space:
        return data

    l = len(value)

    for n in range(0, l, 2):
        if value[n]:
            data[value[n]] = value[n+1]

    return data


def force_use_item_box(value):
    data = []

    if value in space:
        return data

    l = len(value)

    for n in range(0, l, 3):
        reward = value[n]
        num = value[n+1]
        level = value[n+2]
        if reward:
            data.append([force_int_list(level), mapping['list_4'](reward), mapping['int'](num)])

    return data


def force_equip_basis(value):
    data = []

    if value in space:
        return data

    l = len(value)

    for n in range(0, l, 2):
        properties = value[n]
        num = value[n+1]
        if properties and num:
            data.extend([mapping['list_2'](properties), mapping['int_list'](num)])

    return data


def force_guild_info(value):
    data = []

    if value in space:
        return data

    l = len(value)

    for n in range(0, l, 2):
        bar_gacha = value[n]
        bar_num = value[n+1]
        if bar_gacha:
            data.append([mapping['list_2'](bar_gacha), mapping['int'](bar_num)])

    return data


def force_chapter_stage(value):
    data = []

    if value in space:
        return data

    l = len(value)

    for n in range(0, l, 2):
        random_reward = value[n]
        random_num = value[n+1]
        if random_reward:
            data.append([mapping['list_4'](random_reward), mapping['int_list'](random_num)])

    return data


def force_use_item(value):
    if value in space:
        return 0
    if not isinstance(value, basestring):
        return int(value)

    gift = []
    comp = list_compiles[2]
    for v in comp.findall(value):
        gift.append(map(int, v))
    return gift


def force_list_2_to_list(value):
    if value in space:
        return []

    data = []

    max_len = len(value)
    for i in xrange(0, max_len, 2):
        iid, num = value[i:i+2]
        if iid:
            data.append([iid, num])
    return data


def force_list_3_to_list(value):
    if value in space:
        return []

    data = []

    max_len = len(value)
    for i in xrange(0, max_len, 3):
        sort, iid, num = value[i:i+3]
        if sort:
            data.append([sort, iid, num])
    return data


def special_grade_lvlup_badge(config, data):
    uk = data.pop('uk')
    grade = data.pop('grade')
    evolution = data.pop('evolution')

    if uk not in config:
        config[uk] = {}
    if grade not in config[uk]:
        config[uk][grade] = {}

    config[uk][grade][evolution] = {
        'badge': data.pop('badge', {}),
        'cost': data.pop('cost', []),
        'lvl': data.pop('lvl', 0),
    }

    return config


def special_grade_lvlup_reward(config, data):
    uk = data.pop('uk')
    grade = data.pop('grade')
    evolution = data.pop('evolution')

    if uk not in config:
        config[uk] = {}
    if grade not in config[uk]:
        config[uk][grade] = {}
    config[uk][grade][evolution] = data.pop('effect', {})

    return config


def special_rally_checkpoint(config, data):
    rally_id = data.pop('uk')
    check_id = data.pop('check_id')

    if rally_id not in config:
        config[rally_id] = {}
    if check_id not in config[rally_id]:
        config[rally_id][check_id] = {}
    config[rally_id][check_id] = data

    return config


def special_collection_weary(config, data):
    weary = data.pop('uk')
    percent = data.pop('percent')
    if isinstance(config, dict):
        config = []

    config.append((weary, percent))
    config.sort(key=lambda x: x[0], reverse=True)

    return config


def special_manufacture_weary(config, data):
    weary = data.pop('uk')
    percent = data.pop('percent')
    if isinstance(config, dict):
        config = []

    config.append((weary, percent))
    config.sort(key=lambda x: x[0], reverse=True)

    return config


def special_sign_daily_charge(config, data):
    version = data.pop('uk')
    day = data.pop('day')
    if version not in config:
        config[version] = {}

    config[version][day] = data

    return config


def special_add_battle_item(config, data):
    layer = data.pop('uk')
    ring = data.pop('ring')
    battle_id = data.pop('battle_id')
    cost = data.pop('cost')
    if layer not in config:
        config[layer] = {}
    if ring not in config[layer]:
        config[layer][ring] = {'battle_id': [battle_id], 'cost': [cost]}
    else:
        config[layer][ring]['battle_id'].append(battle_id)
        config[layer][ring]['cost'].append(cost)
    return config


def special_battle_item_bank(config, data):
    iid = data.pop('uk')
    layer = data.pop('layer')

    if layer not in config:
        config[layer] = []

    config[layer].append(data)

    return config


def special_battle_item_limit(config, data):
    item_id = data.get('uk')
    quality = data.get('quality')
    sort = data.get('sort')
    quality_item = data.get('quality_item')

    if item_id not in config:
        config[item_id] = {sort: {quality: quality_item}}
    elif sort not in config[item_id]:
        config[item_id][sort] = {quality: quality_item}
    elif quality not in config[item_id][sort]:
        config[item_id][sort][quality] = quality_item

    return config


# def special_robots(config, data):
#     uk = data.pop('uk')
#     lvl = data.pop('lvl')
#     weight = data.pop('weight')
#     hero = data.pop('hero')
#     tools = data.pop('tools')
#
#     if lvl not in config:
#         config[lvl] = []
#     config[lvl].append((uk, hero, tools, weight))
#
#     return config


def specail_pop_uk(replace_key):

    def decorator(config, data):
        value = data.pop('uk')
        data[replace_key] = value
        return data

    return decorator


def last_random_name(config, data):

    last_name = data.get('uk')
    add_dict_list(config, 'last_name', last_name)

    return config


def first_random_name(config, data):

    first_name = data.get('uk')
    add_dict_list(config, 'first_name', first_name)

    return config


def dirtyword(config, data):
    dirtyword = data.get('uk')
    add_dict_list(config, 'dirtyword', dirtyword)

    return config


def int_float_str(value):
    data = None
    if isinstance(value, int):
        data = int(value)
    elif isinstance(value, float):
        if value.is_integer():
            data = int(value)
        else:
            data = float(value)
    else:
        data = force_to_str(value) if value not in space else force_to_str('')

    return str(data)


def force_chapter_enemy(value):
    data = {}
    for i in range(5):
        data.setdefault(i + 1, dict(value[i * 6: i * 6 + 6]))

    return data


def language_zh(config, data):
    _id = data.get('uk')
    translate = data.get('translate')
    add_dict(config, _id, translate)

    return config


def switch_unicode(x):
    if x is not None:
        try:
            x = int(x)
            return repr(int(x))
        except ValueError:
            return force_unicode(x).strip()
    else:
        return ''


def switch_unicode_list(x):
    if x not in space:
        if not isinstance(x, (str, unicode)):
            return [repr(int(x))]

        data = []
        for i in x.split(','):
            try:
                data.append(repr(int(float(i))))
            except ValueError:
                data.append(force_unicode(i).strip())
        return data
    else:
        return []


def battle_story_param(x):
    if x not in space:
        if isinstance(x, float):
            if x.is_integer():
                x = str(int(x))
            else:
                x = str(x)

        if not isinstance(x, (str, unicode)):
            return [repr(int(x))]

        data = []
        for i in x.split(','):
            try:
                data.append(i)
            except ValueError:
                data.append(force_unicode(i).strip())

        return data
    else:
        return []


def force_to_str(x):
    """
    字符串
    :param x:
    :return:
    """
    try:
        x = str(int(x))
    except ValueError:
        x = str(x)

    return force_str(x).strip()


def int_list_to_dict(value):
    """int_list转dict"""
    value = force_int_list(value)
    return dict(enumerate(value))


mapping = {
    # int: 0 or -1 or 1 or '0' or '1' or '-1'
    'int': lambda x: int(x) if x not in space else 0,
    # float: 0.1 or 0.0 or 1.0 or '0.1' or '0.0' or '1.0'
    'float': lambda x: float(x) if x not in space else 0.0,
    # bool: True or False or '' or 'x'
    'bool': lambda x: bool(x) if x not in space else False,
    # str: 字符串
    'str': lambda x: force_to_str(x) if x is not None else force_to_str(''),
    # unicode: 字符串
    'unicode': switch_unicode,
    # int_list: '1,2,3,4,5,-1,0'  [1, 2, 3, 4, 5, -1, 0]
    'int_list': force_int_list,
    # int_list: '1,2,3,4,5,-1,0'  [1, 2, 3, 4, 5, -1, 0]
    'int_or_float_list': force_int_or_float_list,
    # str_list: '1,a'  ['1', 'a']
    'str_list': lambda x: [force_to_str(i.strip()) for i in x.split(',') if i] if x not in space else [],
    # unicode_list: '1,a'  [u'1', u'a']
    'unicode_list': switch_unicode_list,
    'battle_story_param': battle_story_param,
    # mix_str_list: '1,a'  [1, 'a']
    'mix_str_list': force_mix_str_list,
    # mix_unicode_list: '1,a' [1, u'a']
    'mix_unicode_list': force_mix_unicode_list,
    # mix_list_str_list: [1,呜呜,ab],[2,哈哈,abc],[1,呵呵,ab]
    #                    [[1, '\xe5\x91\x9c\xe5\x91\x9c', 'ab'], [2, '\xe5\x93\x88\xe5\x93\x88', 'abc'],
    #                    [1, '\xe5\x91\xb5\xe5\x91\xb5', 'ab']]
    'mix_list_str_list': force_mix_list_str_list,
    # mix_list_unicode_list: [1,呜呜,ab],[2,哈哈,abc],[1,呵呵,ab]
    #                    [[1, u'\u545c\u545c', u'ab'], [2, u'\u54c8\u54c8', u'abc'], [1, u'\u5475\u5475', u'ab']]
    'mix_list_unicode_list': force_mix_list_unicode_list,
    # list_int_list: '[1,2,3],[4,5,6]'   [[1,2],[4,5]]
    'list_int_list': force_list_int_list,
    # int_list_or_int: 1,2 -> [1, 2]  1 -> 1 '' -> [] '[10,10,10],[10,10,10]' -> [[10,10,10],[10,10,10]]
    'int_list_or_int': force_int_list_or_int,
    'int_list_or_int2': force_int_list_or_int2,
    # 2int_list: [1],[1,2] -> [[1], [1,2]]
    '2int_list': force_2int_list,
    # int_float_list_or_int_float: 1,2 -> [1, 2]  1 -> 1 '' -> [] '[10,10,10],[10,10,10]' -> [[10,10,10],[10,10,10]]
    'int_float_list_or_int_float': force_int_float_list_or_int_float,
    # list_1: '[9680],[9801]'   [[9680], [9801]]
    'list_1': force_list(1),
    # list_2: '[9680,9800],[9801,10000]' [[9680, 9800], [9801, 10000]]
    'list_2': force_list(2),
    # list_3: '[9680,9800,70],[9801,10000,15]' [[9680, 9800, 70], [9801, 10000, 15]]
    'list_3': force_list(3),
    # list_4: '[9680,9800,70,70],[9801,10000,15,30]' [[9680, 9800, 70, 70], [9801, 10000, 15, 30]]
    'list_4': force_list(4),
    # list_5: '[9680,9800,70,70,70],[9801,10000,15,30,30]' [[9680, 9800, 70, 70, 70], [9801, 10000, 15, 30, 30]]
    'list_5': force_list(5),
    # list_6: '[7,9680,9800,70,70,70],[7,9801,10000,15,30,30]' [[7,9680, 9800, 70, 70, 70], [7,9801, 10000, 15, 30, 30]]
    'list_6': force_list(6),
    # '[1,1],[2,2]' -> [[1,1],[2,2]]  1 -> 1
    'use_item': force_use_item,
    'mult_dict_0': force_mult_dict(0),
    'mult_dict_1': force_mult_dict(),
    'mult_dict_2': force_mult_dict(2),
    'mult_dict_12': force_mult_dict(12),
    'mult_key_dict': force_mult_key_dict,
    'mult_list': force_mult_list,
    'mult_list1': force_mult_list1,
    'mult_force_num_list': force_mult_force_num_list,
    'list_2_to_dict': force_list_2_to_dict,
    'use_item_box': force_use_item_box,
    'equip_basis': force_equip_basis,
    'guild_info': force_guild_info,
    'chapter_stage': force_chapter_stage,
    'grade_lvlup_badge': special_grade_lvlup_badge,
    'grade_lvlup_reward': special_grade_lvlup_reward,
    'rally_checkpoint': special_rally_checkpoint,
    'collection_weary': special_collection_weary,
    'manufacture_weary': special_manufacture_weary,
    'sign_daily_charge': special_sign_daily_charge,
    'add_battle_item': special_add_battle_item,
    'battle_item_bank': special_battle_item_bank,
    'battle_item_limit': special_battle_item_limit,
    # 'robots': special_robots,
    'last_random_name': last_random_name,
    'first_random_name': first_random_name,
    'list_2_to_list': force_list_2_to_list,
    'list_3_to_list': force_list_3_to_list,
    'grade_guild_build': specail_pop_uk('lv'),
    'guild_protect_money': specail_pop_uk('hire_basis'),
    'dict': lambda x: dict(x) if x else {},
    # int_float_str: 1 or 1.0 -> 1, 1.1 -> 1.1 其他-> str
    'int_float_str': int_float_str,
    'chapter_enemy': force_chapter_enemy,
    'dirtyword': dirtyword,
    'guild_war': specail_pop_uk('num_limit'),
    'int_str': lambda x: str(int(x)) if x else '',
    'initial_account': specail_pop_uk('level'),
    'language_zh': language_zh,
    'int_list_to_dict': int_list_to_dict,
    'buy_silver': specail_pop_uk('id'),
}

