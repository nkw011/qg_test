import re

def remove_html(text):
    text = re.sub(r"<[^>]+>\s+(?=<)|<[^>]+>", "", text).strip()
    return text


def remove_email(text):
    text = re.sub(r"[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "", text).strip()
    return text


def remove_hashtag(text):
    text = re.sub(r"#\S+", "", text).strip()
    return text


def remove_user_mention(text):
    text = re.sub(r"@\w+", "", text).strip()
    return text


def remove_url(text):
    """
    URL을 제거합니다.
    ``주소: www.naver.com`` -> ``주소: ``
    """
    text = re.sub(r"(http|https)?:\/\/\S+\b|www\.(\w+\.)+\S*", "", text).strip()
    text = re.sub(r"pic\.(\w+\.)+\S*", "", text).strip()
    return text


def remove_bad_char(text):
    """
    문제를 일으킬 수 있는 문자들을 제거합니다.
    """
    bad_chars = {"\u200b": "", "…": " ... ", "\ufeff": ""}  # 가끔씩 생길 수 있는 이상한 문자들
    for bad_char in bad_chars:
        text = text.replace(bad_char, bad_chars[bad_char])
    text = re.sub(r"[\+á?\xc3\xa1]", "", text)
    return text


def remove_press(text):
    """
    언론 정보를 제거합니다.
    ``홍길동 기자 (연합뉴스)`` -> ````
    ``(이스탄불=연합뉴스) 하채림 특파원 -> ````
    """
    re_patterns = [
        r"\([^(]*?(뉴스|경제|일보|미디어|데일리|한겨례|타임즈|위키트리)\w+?\)",
        r"[가-힣]{0,4} (기자|선임기자|수습기자|특파원|객원기자|논설고문|통신원|연구소장) ",  # 이름 + 기자
        r"[가-힣]{1,}(뉴스|경제|일보|미디어|데일리|한겨례|타임|위키트리)",  # (... 연합뉴스) ..
        r"\(\s+\)",  # (  )
        r"\(=\s+\)",  # (=  )
        r"\(\s+=\)",  # (  =),
        r"\([^(]*?(뉴스|경제|일보|미디어|데일리|한겨례|타임즈|위키트리)[\w\W]*?\)"  # 자체 제작, (사진=위키트리, 무단 전재-재배포 금지) 제거
    ]

    re_patterns2 = [
        r"\<저작권자(\(c\)|ⓒ|©|\(Copyright\)|(\(c\))|(\(C\))).+?\>",
        r"저작권자\(c\)|ⓒ|©|(Copyright)|(\(c\))|(\(C\))"
    ]

    for re_pattern in re_patterns:
        text = re.sub(re_pattern, "", text).strip()

    for re_pattern in re_patterns2:
        text = re.sub(re_pattern, "", text).strip()

    text = re.sub(r"\(출처 ?= ?.+\) |\(사진 ?= ?.+\) |\(자료 ?= ?.+\)| \(자료사진\) |사진=.+기자 ", "", text).strip()
    return text


def clean_punc(text):
    punct_mapping = {"‘": "'", "₹": "e", "´": "'", "°": "", "€": "e", "™": "tm", "√": " sqrt ", "×": "x", "²": "2",
                     "—": "-", "–": "-", "’": "'", "_": "-", "`": "'", '“': '"', '”': '"', '“': '"', "£": "e",
                     '∞': 'infinity', 'θ': 'theta', '÷': '/', 'α': 'alpha', '•': '.', 'à': 'a', '−': '-', 'β': 'beta',
                     '∅': '', '³': '3', 'π': 'pi', }

    for p in punct_mapping:
        text = text.replace(p, punct_mapping[p])
    text = text.strip()

    return text


def remove_extra(text):
    re_pattern = r'○|㈜|\(재\)|\(주\)|\n|<|>|▲|《|》|＜|＞'
    re_pattern2 = r'、|。|·|‥|…|¨|〃|―|∥|＼|∼|‘|’|“|”|〔|〕|〈|〉|《|》|「|」|『|』|【|】|±|×|÷|≠|≤|≥|∞|∴|°|′|″|℃|Å|￠|￡|￥|♂|♀|∠|⊥|⌒|∂|∇|≡|≒|§|※|☆|★|○|●|◎|◇|◆|□|■|△|▲|▽|▼|→|←|↑|↓|↔|〓|≪|≫|√|∽|A1F|∝|∵|∫|∬|∈|∋|⊆|⊇|⊂|⊃|∪|∩|∧|∨|￢'
    re_pattern3 = r'⇒|⇔|∀|∃|´|～|ˇ|˘|˝|˚|˙|¸|˛|¡|¿|ː|∮|∑|∏|¤|℉|‰|◁|◀|▷|▶|♤|♠|♡|♥|♧|♣|⊙|◈|▣|◐|◑|▒|▤|▥|▨|▧|▦|▩|♨|☏|☎|☜|☞|¶|†|‡|↕|↗|↙|↖|↘|♭|♩|♪|♬|㉿|㈜|№|㏇|™|㏂|㏘|℡|€|®|㉾'

    text = re.sub(re_pattern, "", text).strip()
    text = re.sub(re_pattern2, "", text).strip()
    text = re.sub(re_pattern3, "", text).strip()

    return text


def remove_language(range_s, range_e, sentence):
    a = int(range_s, 16)  # 16진수 -> 10진수 변환
    b = int(range_e, 16)
    return_sentence = ''
    for i, w in enumerate(sentence):
        if a <= ord(w) and ord(w) <= b:  # 음절 단위로 사전에 정의한 유니코드 범위 내에 존재하는가
            continue
        return_sentence += w
    return return_sentence


def remove_hanja(text):
    text = remove_language('2E80', '2EFF', text)
    text = remove_language('3400', '4DBF', text)
    text = remove_language('4E00', '9FBF', text)
    text = remove_language('F900', 'FAFF', text)
    text = remove_language('20000', '2A6DF', text)
    text = remove_language('2F800', '2F800', text)

    return text


def remove_repeated_spacing(text):
    """
    두 개 이상의 연속된 공백을 하나로 치환합니다.
    ``오늘은    날씨가   좋다.`` -> ``오늘은 날씨가 좋다.``
    """

    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_bracket_string(text):
    bracket_pattern1 = re.compile(r"\((.*?)\)")
    bracket_pattern2 = re.compile(r"\[(.*?)\]")

    text = re.sub(bracket_pattern1, '', text)
    text = re.sub(bracket_pattern2, '', text)

    text = re.sub(r"\(\)", '', text)
    text = re.sub(r"\[\]", '', text)

    return text


def remove_useless_breacket(text):
    """
    위키피디아 전처리를 위한 함수입니다.
    괄호 내부에 의미가 없는 정보를 제거합니다.
    아무런 정보를 포함하고 있지 않다면, 괄호를 통채로 제거합니다.
    ``수학(,)`` -> ``수학``
    ``수학(數學,) -> ``수학(數學)``
    """
    bracket_pattern = re.compile(r"\((.*?)\)")

    modi_text = ""
    text = text.replace("()", "")  # 수학() -> 수학
    brackets = bracket_pattern.search(text)

    if not brackets:
        return text

    replace_brackets = {}
    # key: 원본 문장에서 고쳐야하는 index, value: 고쳐져야 하는 값
    # e.g. {'2,8': '(數學)','34,37': ''}
    while brackets:
        index_key = str(brackets.start()) + "," + str(brackets.end())
        bracket = text[brackets.start() + 1: brackets.end() - 1]
        infos = bracket.split(",")
        modi_infos = []
        for info in infos:
            info = info.strip()
            if len(info) > 0:
                modi_infos.append(info)
        if len(modi_infos) > 0:
            replace_brackets[index_key] = "(" + ", ".join(modi_infos) + ")"
        else:
            replace_brackets[index_key] = ""
        brackets = bracket_pattern.search(text, brackets.start() + 1)
    end_index = 0
    for index_key in replace_brackets.keys():
        start_index = int(index_key.split(",")[0])
        modi_text += text[end_index:start_index]
        modi_text += replace_brackets[index_key]
        end_index = int(index_key.split(",")[1])
    modi_text += text[end_index:]
    modi_text = modi_text.strip()

    return modi_text


def korean_preprocess(example):
    text = example['context']
    func_list = [remove_html, remove_email, remove_hashtag,
                 remove_user_mention, remove_url, remove_bad_char,
                 remove_press, clean_punc, remove_extra,
                 remove_repeated_spacing, remove_useless_breacket]
    for func in func_list:
        text = func(text)
    example['context'] = text

    return example