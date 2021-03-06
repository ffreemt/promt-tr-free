'''
promt translate for free as in beer
'''

from typing import Any, Callable, Dict, Tuple

import sys
import logging
import json
from time import time
from random import randint
import pytest  # type: ignore
# import mock
import urllib3

from ratelimit import limits, sleep_and_retry  # type: ignore
import requests
from fuzzywuzzy import fuzz, process  # type: ignore
import coloredlogs  # type: ignore
from jmespath import search  # type: ignore

urllib3.disable_warnings()
# logging.captureWarnings(True)
# logging.getLogger('requests.packages.urllib3.connectionpool').level = 30

LOGGER = logging.getLogger(__name__)
FMT = '%(filename)-14s[%(lineno)-3d] %(message)s [%(funcName)s]'
coloredlogs.install(level=20, logger=LOGGER, fmt=FMT)

# en-ar en-zhcn
LANG_CODES = (
    "ar,ca,zhcn,nl,fi,fr,de,el,he,hi,it,ja,kk,ko,pt,ru,es,tr,uk"
).split(',') + ['auto']

URL = (
    'https://www.online-translator.com/'
    'services/soap.asmx/GetTranslation'
)
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17'  # noqa
# HEADERS = {"User-Agent": UA}
HEADERS = {
    'Host': 'www.online-translator.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Content-Type': 'application/json; charset=utf-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://www.online-translator.com',
    # 'DNT': '1',
    'Referer': 'https://www.online-translator.com/',
}

SESS = requests.Session()
SESS.get('https://www.online-translator.com/', verify=0)


def with_func_attrs(**attrs: Any) -> Callable:
    ''' with_func_attrs '''
    def with_attrs(fct: Callable) -> Callable:
        for key, val in attrs.items():
            setattr(fct, key, val)
        return fct
    return with_attrs


@with_func_attrs(text='')
def _promt_tr(
        text: str,
        from_lang: str = 'auto',
        to_lang: str = 'zh',
        timeout: Tuple[float, float] = (55, 66),
) -> Dict[str, str]:
    ''' promt_tr

    text = 'test one two three'
    from_lang = 'auto'
    to_lang = 'zh'
    timeout = (55, 66)
    '''

    try:
        from_lang = from_lang.lower()
    except Exception as exc:  # pragma: no cover
        LOGGER.warning("%s", exc)
        from_lang = 'auto'
    try:
        to_lang = to_lang.lower()
    except Exception as exc:  # pragma: no cover
        LOGGER.warning("%s", exc)
        to_lang = 'zh'

    if from_lang in ['zh', 'chinese', 'zhongwen']:
        from_lang = 'zhcn'
    if to_lang in ['zh', 'chinese', 'zhongwen']:
        to_lang = 'zhcn'

    try:
        from_lang = process.extractOne(from_lang, LANG_CODES, scorer=fuzz.UWRatio)[0]  # noqa
    except Exception as exc:  # pragma: no cover
        LOGGER.warning("%s", exc)
        from_lang = 'en'
    try:
        to_lang = process.extractOne(to_lang, LANG_CODES, scorer=fuzz.UWRatio)[0]  # noqa
    except Exception as exc:  # pragma: no cover
        LOGGER.warning("%s", exc)
        to_lang = 'en'

    if from_lang == 'auto':
        from_lang = 'au'
    if to_lang == 'auto':  # pragma: no cover
        to_lang = 'au'

    dir_code = f'{from_lang}-{to_lang}'
    data = {
        'dirCode': dir_code,
        # 'dirCode': 'de-en',
        'template': 'General',
        # 'text': 'Das sind drei Teste.',
        'text': text,
        'lang': 'en',
        'limit': '3000',
        'useAutoDetect': True,
        'key': '123',
        'ts': 'MainSite',
        'tid': '',
        'IsMobile': False
    }

    try:
        resp = SESS.post(  # type: ignore  # data  # expected "Union[None, bytes, MutableMapping[str, str], IO[Any]]  # noqa
            URL,
            # data=data2,
            data=json.dumps(data),
            headers=HEADERS,
            timeout=timeout,
        )
        resp.raise_for_status()
    except Exception as exc:  # pragma: no cover
        LOGGER.error('%s', exc)
        resp = requests.models.Response()
        resp._content = f'{{"errorCode": "{exc}"}}'.encode()
        resp.status_code = 499
    try:
        jdata = resp.json()
    except Exception as exc:  # pragma: no cover
        LOGGER.error('%s', exc)
        jdata = {'error': str(exc)}

    promt_tr.text = resp.text

    try:
        # res = search('[0].translations[0].text', jdata)
        res = search('d.result', jdata)
    except Exception as exc:  # pragma: no cover
        LOGGER.error('%s', exc)
        res = {'error': str(exc)}

    return res


@sleep_and_retry
@limits(calls=30, period=20, raise_on_limit=True)  # raise_on_limit probably superfluous
def _rl_promt_tr(*args, **kwargs):
    ''' be nice and throttle'''
    LOGGER.info(' rate limiting 3 calls/2 secs... ')
    return _promt_tr(*args, **kwargs)


@with_func_attrs(calls=0, call_tick=-1)
def promt_tr(*args, **kwargs):
    ''' exempt first 200 calls from rate limiting '''

    # increase calls unto 210
    if promt_tr.calls < 210:
        promt_tr.calls += 1

    # reset rate limit if the last call was 2 minutes ago
    tick = time()
    if tick - promt_tr.call_tick > 120:
        promt_tr.calls = 1
    promt_tr.call_tick = tick

    if promt_tr.calls < 200:
        return _promt_tr(*args, **kwargs)

    return _rl_promt_tr(*args, **kwargs)


@pytest.mark.parametrize(
    # 'to_lang', LANG_CODES
    'to_lang', ['zh', 'de', 'fr', 'it', 'ko', 'ja', 'ru']
)
def test_sanity(to_lang):
    'sanity test'

    numb = str(randint(1, 10000))
    text = 'test ' + numb
    assert numb in promt_tr(text, to_lang=to_lang)


def test_calls():
    ''' test calls '''
    _ = promt_tr('test ')
    calls = promt_tr.calls
    _ = promt_tr('test ')
    assert promt_tr.calls == calls + 1


def main():  # pragma: no cover
    ''' main '''

    text = sys.argv[1:]
    text1 = ''
    if not text:
        print(' Provide something to translate, testing with some random text\n')
        text = 'test tihs and that' + str(randint(1, 1000))
        text1 = 'test tihs and that' + str(randint(1, 1000))

    print(f'{text} translated to:')
    for to_lang in ['zh', 'de', 'fr', ]:
        print(f'{to_lang}: {promt_tr(text, to_lang=to_lang)}')
        if not text1:
            print(f'{to_lang}: {promt_tr(text1, to_lang=to_lang)}')


def init():
    ''' attempted to pytest __name__ == '__main__' '''
    LOGGER.debug('__name__: %s', __name__)
    if __name__ == '__main__':
        sys.exit(main())


init()

# test_init()
