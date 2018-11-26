# -*- coding: utf-8 –*-

import json
import pstats
import settings
import traceback
import cStringIO
import importlib
import tornado.web
import handler_tools
import tornado.websocket
import cProfile as profile
from gconfig import game_config
from models.logging import Logging
from lib.statistics.dmp import stat
from lib.utils.debug import print_log
from lib.utils.debug import error_mail
from lib.core.environ import HandlerManager
from lib.utils.redis_netlock import MyRedisLock
from lib.core.handlers.htornado import BaseRequestHandler

get_msg_str = game_config.get_lan_error_msg


def lock(func):
    ignore_api_module = []
    ignore_api_method = []

    def error(handler, msg=''):
        d = {
            'status': 9999,
            'data': {},
            'msg': msg,
            'user_status': {},
        }

        r = json.dumps(d, ensure_ascii=False, encoding='utf-8', indent=2)
        handler.write(r)
        handler.finish()

    def wrapper(handler, *args, **kwargs):
        if handler.hm is None:
            error(handler, 'hm is none')
            return

        method_param = handler.hm.req.get_argument('method')
        module_name, method_name = method_param.split('.')

        result = 0, {}
        if not settings.DEBUG and handler.hm.mm and module_name not in ignore_api_module \
                and method_param not in ignore_api_method:
            user = handler.hm.mm.user
            _client = user.redis
            lock_key = user.make_key_cls('lock.%s' % user.uid, user._server_name)
            lock = MyRedisLock(lock_key, _client, ex=1, retry=False)
            with lock as f:
                if not f:
                    error(handler, 'user key is locked')
                else:
                    result = func(handler, *args, **kwargs)
        else:
            result = func(handler, *args, **kwargs)

        return result

    return wrapper


class APIRequestHandler(BaseRequestHandler):
    """ 全部API处理公共接口
    """
    # 判断重试接口 可忽略的接口、模块
    retry_api_ignore_api_module = []
    retry_api_ignore_api_method = []

    # 主线、支线任务自动领取接口
    AUTO_RECEIVE_MISSION_AWARD_FUNC = ['user.main', 'user.talk_npc']
    # 主线、支线任务
    MISSION_TASK_UPDATE_FUNC = ['user.buy_point', 'user.buy_silver', 'private_city.sweep', 'shop.buy']

    @error_mail(not settings.MAIL_SENDING, settings.ADMIN_LIST)
    def initialize(self):
        self.hm = HandlerManager(self)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    def result_info(self, rc, data=None):
        """ 返回信息

        :param rc:
        :param data:
        :return:
        """
        msg = ''
        if data is None:
            data = {}

        if rc:
            if data:
                msg = data.get('custom_msg')
            if not msg:
                msg = get_msg_str(self.get_argument('lan', '0')).get(rc)
            if not msg:
                method_param = self.get_argument('method')
                msg = get_msg_str(self.get_argument('lan', '0')).get(method_param, {}).get(rc, method_param + '_error_%s' % rc)

        return rc, data, msg, self.hm.mm

    @lock
    def handler(self):
        """ 处理

        :return:
        """
        method_param = self.get_argument('method')
        module_name, method_name = method_param.split('.')
        # 每个请求生成的时间戳
        __ts = self.get_argument('__ts', '')

        retry_api_flag = '%s%s' % (method_param, __ts)

        # 判断是否是重试api
        user_logging = Logging(self.hm.uid)
        if self.get_argument('kvretry', ''):
            last_api_data = user_logging.get_last_api_data()
            if last_api_data:
                if last_api_data['m'] == retry_api_flag:
                    self.set_header('Content-Type', 'application/json; charset=UTF-8')
                    self.write(last_api_data['d'])
                    self.finish()
                    return

        ################## 线上分析接口性能 ###########################
        if self.get_argument('__check_profile', ''):
            prof = profile.Profile()
            prof.runctx('rc, data, msg, mm = self.api()', globals(), locals())

            out = cStringIO.StringIO()
            stats = pstats.Stats(prof)
            stats.stream = out
            stats.strip_dirs().sort_stats(2).print_stats()

            result = out.getvalue()
            self.write(result)
            self.finish()
            return
        ################## 线上分析接口性能 ###########################

        rc, data, msg, mm = self.api()
        result = handler_tools.result_generator(rc, data, msg, mm)

        # 记录最后一次api返回数据
        if rc == 0:
            if module_name not in self.retry_api_ignore_api_module and \
                            method_param not in self.retry_api_ignore_api_method:
                user_logging.add_last_api_data(retry_api_flag, result)

        try:
            self.write(result)
        finally:
            self.finish()

    def handler_error(self, rc):
        """

        :param rc:
        :return:
        """
        rc, data, msg, mm = self.result_info(rc)
        result = handler_tools.result_generator(rc, data, msg, mm)
        try:
            self.write(result)
        finally:
            self.finish()

    @stat
    def api(self):
        """ API统一调用方法
        """
        user = self.hm.mm.user

        """
        # ########## 封号 start #################
        ban_info = user.get_ban_info()
        if ban_info:
            return self.result_info('error_17173', {'custom_msg': ban_info})
        # ########## 封号 end #################

        # ########## 封ip start #################
        uip = self.hm.req.request.headers.get('X-Real-Ip', '') or self.hm.req.request.remote_ip
        banip_info = user.get_banip_info(uip)
        if banip_info:
            return self.result_info('error_17173', {'custom_msg': banip_info})
        # ########## 封ip end #################
        """

        method_param = self.get_argument('method')
        module_name, method_name = method_param.split('.')

        try:
            module = importlib.import_module('views.%s' % module_name)
        except ImportError:
            print_log(traceback.print_exc())
            return self.result_info('error_module')

        method = getattr(module, method_name, None)
        if method is None:
            return self.result_info('error_method')

        if callable(method):
            pre_status, pre_data = self.pre_handler()
            if pre_status:
                return self.result_info(pre_status, pre_data)

            rc, data = method(self.hm)
            # call_status 只有rc不为0时, 可以传call_status True: 代表执行成功  False: 代表执行失败
            if rc != 0 and not data.get('call_status', False):
                return self.result_info(rc, data)

            post_status = self.post_handler()
            if post_status:
                return self.result_info(post_status, data)

            client_cache_udpate = {}
            old_data = {}

            if self.hm.mm:
                if method_param not in ['user.get_red_dot', 'user.game_info']:
                    cur_lan_sort = self.get_argument('lan', '1')
                    if cur_lan_sort != self.hm.mm.user.language_sort:
                        self.hm.mm.user.language_sort = cur_lan_sort
                    self.hm.mm.user.update_active_time(self.request)
                    self.hm.mm.user.save()

                """
                # 主线任务，支线任务自动领奖
                mission_award = {}
                if method_param in self.AUTO_RECEIVE_MISSION_AWARD_FUNC:
                    mission_award = self.hm.mm.mission_main.auto_receive_award()
                    if mission_award:
                        data['_mission_main'] = mission_award

                if mission_award or method_param in self.MISSION_TASK_UPDATE_FUNC:
                    data['mission_task'] = self.hm.mm.mission_main.get_main_tasks()
                    data['side_task'] = self.hm.mm.mission_side.get_side_tasks(filter=True)
                """
                # 执行成功保存数据
                self.hm.mm.do_save()

                # 关于客户端数据缓存的更新
                for k, obj in self.hm.mm._model.iteritems():
                    if obj and obj.uid == self.hm.uid and getattr(obj, '_diff', None):
                        client_cache_udpate[obj._model_name] = obj._client_cache_update()
                        old_data[k] = getattr(obj, '_old_data', {})

            data['_client_cache_update'] = client_cache_udpate
            data['old_data'] = old_data
            return self.result_info(rc, data)
        return self.result_info('error_not_call_method')

    def pre_handler(self):
        """ 处理方法之前

        :return:
        """
        # DEBUG模式, 验证失效
        if settings.DEBUG:
            return 0, None

        # 验证是否是浏览器
        user_agent = self.request.headers.get('User-Agent')
        browser = self.get_argument('browser', '') == settings.BROWSER
        if not browser and (user_agent is not None or not self.get_argument('method')):
            return 'error_9999', None

        # 强制更新
        version = self.hm.get_argument('version', '')
        tpid = self.hm.mm.user.tpid
        version_config = game_config.version.get(str(tpid), game_config.version.get('all'))
        if version_config and version_config['version'] > version:
            return 'error_9998', {
                'custom_msg': version_config['msg'],
                'client_upgrade': {
                    'url': version_config['url'],
                    'msg': version_config['msg'],
                },
            }

        # 封号
        if self.hm.mm.user.is_ban:
            return 'error_9997', None

        # # 多点登录
        # ks = self.hm.get_argument('ks', '', strip=False)
        # mk = self.hm.get_argument('mk', '')
        # frontwindow = self.hm.get_argument('frontwindow', '') == settings.FRONTWINDOW
        # if not frontwindow and (self.hm.mm.user.mk != mk or self.hm.mm.user.session_expired(ks)):
        #     return 'error_9527', None

        return 0, None

    def post_handler(self):
        """ 处理方法之后

        :return:
        """

        return 0

    @tornado.web.asynchronous
    @error_mail(not settings.MAIL_SENDING, settings.ADMIN_LIST)
    def get(self):
        """ 处理GET请求
        """
        if self.hm is None or self.hm.mm is None:
            self.handler_error('error_100')
            return None

        self.handler()

    @tornado.web.asynchronous
    @error_mail(not settings.MAIL_SENDING, settings.ADMIN_LIST)
    def post(self):
        """ 处理POST请求
        """
        if self.hm is None or self.hm.mm is None:
            self.handler_error('error_100')
            return None

        self.handler()



