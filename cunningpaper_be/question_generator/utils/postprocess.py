from kiwipiepy import Kiwi

answer_tag = {'SP', 'XSN', 'SN', 'SF',
              'NNP', 'NR', 'SL', 'NP',
              'SSO', 'SW', 'W_HASHTAG',
              'SO', 'W_SERIAL', 'SSC', 'NNG',
              'SS', 'NNB', 'SH', 'XPN'}

def keyword_post_process(tagger:Kiwi, text: str, answer_tag:set = answer_tag):
    post = []
    for token in tagger.tokenize(text):
        if token.tag in answer_tag:
            post.append(token)
        else:
            break
    if not post:
        return ""
    last = 0
    for token in post:
        last = token.start + token.len
    return text[:last]

if __name__== "__main__":
    kiwi = Kiwi()
    text = "귀도 반 로섬"
    print(keyword_post_process(kiwi, text))
