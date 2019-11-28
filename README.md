# promt-tr-free

Promt translate for free: be gentle and rate-limit to 3 calls/2 seconds, first 200 calls exempted

### Installation

```pip install -U promt-tr-free```

or

* Install (pip or whatever) necessary requirements, e.g. ```
pip install requests fuzzywuzzy pytest jmespath coloredlogs``` or ```
pip install -r requirements.txt```
* Drop the file promt_tr.py in any folder in your PYTHONPATH (check with import sys; print(sys.path)
* or clone the repo (e.g., ```git clone https://github.com/ffreemt/promt-tr-free.git``` or download https://github.com/ffreemt/promt-tr-free/archive/master.zip and unzip) and change to the promt-tr-free folder and do a ```
python setup.py develop```

### Usage

```
from promt_tr import promt_tr

print(promt_tr('hello world', to_lang='de'))  # ->'hallo Welt'
print(promt_tr('hello world', to_lang='fr'))  # ->'bonjour monde'
print(promt_tr('hello world', to_lang='ja'))  # ->'ハロー・ワールド'
print(promt_tr('世界您好', to_lang='ja'))  # ->'ハロー・ワールド'
print(promt_tr('世界您好', to_lang='en'))  # ->'Hello world'
print(promt_tr('Diese sind Teste', to_lang='zh'))  # ->'这是测试'
```

Languages supported: ar, ca, zhcn, nl, fi, fr, de, el, he, hi, it, ja, kk, ko, pt, ru, es, tr, uk.
Consult the official website for details.

### Acknowledgments

* Thanks to everyone whose code was used
