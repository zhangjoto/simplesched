#!/usr/bin/env python
#
# Author: Zhang Zhen
# E-Mail: zhangjoto@gmail.com
#
# Create Date: 2018-09-15
#

import importlib
import logging
import sched
import time

import yaml

from . import utils

logger = logging.getLogger(__name__)


class BaseScheduler:
    """执行小型定期任务、周期任务的基本类。

    执行任务时需要的外部资源由名为 context 的 mapper 参数传入，包括但
    不限于数据库连接等。
    对外发送任务执行结果则由传入的 sender （实例化）对象执行，该对象应
    有 send 方法。
    读取的配置文件格式如 tests/tasks.yml.sample 文件所示。"""
    # TODO: daemonize
    # TODO: hot reload，两套配置定期切换需要此功能支持

    def __init__(self, config_file='tests/tasks.yml.sample', sender=None,
                 context=None):
        """测试 docstring"""
        self.conf = self.load_conf(config_file)
        self.scheder = sched.scheduler(time.time, time.sleep)
        self.sender = sender
        self.ctx = context

    def load_conf(self, fname):
        with open(fname) as fp:
            conf = yaml.load(fp.read())
            try:
                conf['default']['to']['error']
            except (KeyError, TypeError):
                logger.error('key default->to->error missing.')
                raise SystemExit(1)

        # 将配置中的默认属性展开到每个任务，便于使用
        for actor in conf['actors']:
            for key in ('module', 'priority', 'interval'):
                if key not in actor:
                    actor[key] = conf['default'][key]
        logger.debug(conf)
        return conf

    def one_task_reg(self, task):
        """运行任务，并将下次运行的时间注册到待运行队列。"""

        prior = task['priority']

        # 每次执行任务之前要将下次任务加入执行队列，以避免运行时间逐渐偏移
        if task['trigger'] == 'interval':  # 周期性运行的任务
            interval = task['interval']
            self.scheder.enter(interval, prior, self.one_task_reg, (task,))
        else:  # 在指定时间点运行的任务
            nexttime = utils.next_time(task['times'])
            self.scheder.enterabs(nexttime, prior, self.one_task_reg, (task,))
        return self.task_wrapper(task)

    def task_no_exception(self, one_task):
        """根据配置项加载任务函数。

        使用闭包包装动作函数，目的是捕捉所有异常，避免外部代码质量导致
        进程退出，并保证发送异常情况通知。"""
        module_name = one_task['module']
        module = importlib.import_module(module_name)
        action = getattr(module, one_task['program'])

        def func(*args):
            try:
                return action(*args)
            except Exception as err:
                logger.exception(err)
                self.sender.send(
                    self.conf['default']['to']['error'],
                    'From {}: {} error: {}'.format(
                        self.conf['identifier'],
                        one_task['program'], str(err)))
        return func

    def all_task_reg(self):
        for task in self.conf['actors']:
            logger.debug('wrapper action: %s', task['program'])
            task['wrapped'] = self.task_no_exception(task)
            self.one_task_reg(task)

    def task_wrapper(self, task):
        pack = task['wrapped'](self.ctx, *task['arguments'])
        if pack:
            pack = 'From {}: {}'.format(self.conf['identifier'], pack)
            logger.debug('pack: %s', pack)
            to = task.get('to', self.conf['default']['to']['normal'])
            self.sender.send(to, pack)

    def run(self):
        self.all_task_reg()
        self.scheder.run()
