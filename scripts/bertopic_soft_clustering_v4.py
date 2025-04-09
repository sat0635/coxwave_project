import json
import re
from collections import Counter

from bertopic import BERTopic
from kiwipiepy import Kiwi
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer

kiwi = Kiwi()
input_file = "faq_answer_question_pair.jsonl"
output_file = "faq_answer_question_pair_with_categories_v4.jsonl"

data = []
texts = []

# ref https://gist.github.com/spikeekips/40eea22ef4a89f629abd87eed535ac6a
korean_stopwords = [
    "해당",
    "가",
    "가까스로",
    "가령",
    "각",
    "각각",
    "각자",
    "같다",
    "같이",
    "것",
    "것들",
    "게다가",
    "겨우",
    "결국",
    "결론을 낼 수 있다",
    "결과에 이르다",
    "고려하면",
    "곧",
    "공동으로",
    "과",
    "과연",
    "관계가 있다",
    "관계없이",
    "관련이 있다",
    "관하여",
    "관한",
    "구체적으로",
    "그",
    "그들",
    "그때",
    "그래",
    "그래서",
    "그러나",
    "그러니까",
    "그러면",
    "그러므로",
    "그런데",
    "그렇지만",
    "그리고",
    "그리하여",
    "그에 따르는",
    "그저",
    "근거로",
    "근거하여",
    "기준으로",
    "기타",
    "까지",
    "까지도",
    "나",
    "나머지는",
    "남들",
    "너",
    "너희",
    "너희들",
    "네",
    "년",
    "논하지 않다",
    "누구",
    "다른",
    "다만",
    "다소",
    "다시 말하자면",
    "다시말하면",
    "다음",
    "다음에",
    "단지",
    "당신",
    "당장",
    "대로 하다",
    "대하면",
    "대하여",
    "대해서",
    "더구나",
    "더군다나",
    "더라도",
    "더불어",
    "더욱더",
    "동안",
    "된바에야",
    "된이상",
    "두번째로",
    "뒤따라",
    "뒤이어",
    "등",
    "등등",
    "따라",
    "따라서",
    "따위",
    "때",
    "때문에",
    "또",
    "또는",
    "또한",
    "마치",
    "만약",
    "만일",
    "만큼",
    "말하자면",
    "말할것도 없고",
    "매번",
    "몇",
    "모두",
    "무엇",
    "무슨",
    "무엇때문에",
    "물론",
    "및",
    "바꾸어말하자면",
    "바로",
    "반대로",
    "반드시",
    "보다더",
    "본대로",
    "부터",
    "불구하고",
    "비교적",
    "비로소",
    "비록",
    "비하면",
    "뿐만 아니라",
    "뿐이다",
    "사람",
    "상대적으로 말하자면",
    "생각한대로",
    "설사",
    "설령",
    "소인",
    "수",
    "시간",
    "시작하여",
    "시초에",
    "실로",
    "심지어",
    "아니",
    "아니라면",
    "아니면",
    "아래윗",
    "아무거나",
    "아무도",
    "아야",
    "아울러",
    "앞에서",
    "약간",
    "양자",
    "어느",
    "어느쪽",
    "어디",
    "어떻게",
    "어찌",
    "언제",
    "얼마",
    "얼마나",
    "얼마든지",
    "여기",
    "여러분",
    "여섯",
    "여전히",
    "연관되다",
    "영차",
    "예",
    "예를 들면",
    "예를 들자면",
    "오로지",
    "오직",
    "오히려",
    "와",
    "왜",
    "왜냐하면",
    "우르르",
    "우리",
    "우리들",
    "우선",
    "우에 종합한것과같이",
    "운운",
    "위에서 서술한바와같이",
    "위하여",
    "위해서",
    "의",
    "의거하여",
    "의지하여",
    "의해",
    "의해서",
    "이",
    "이 되다",
    "이 때문에",
    "이 밖에",
    "이 외에",
    "이것",
    "이것들",
    "이곳",
    "이때",
    "이래",
    "이러한",
    "이런",
    "이럴정도로",
    "이렇게",
    "이리하여",
    "이번",
    "이상",
    "이어서",
    "이었다",
    "이와 같다",
    "이와 같은",
    "이와 반대로",
    "이와같다면",
    "이용하여",
    "이유만으로",
    "이젠",
    "이지만",
    "이쪽",
    "인 듯하다",
    "일",
    "일단",
    "일반적으로",
    "일지라도",
    "임에 틀림없다",
    "입각하여",
    "입장에서",
    "있다",
    "자기",
    "자기집",
    "자신",
    "잠깐",
    "저",
    "저기",
    "저쪽",
    "저희",
    "전부",
    "전자",
    "전후",
    "점에서 보아",
    "정도에 이르다",
    "제외하고",
    "조금",
    "조차",
    "조차도",
    "좀",
    "좋아",
    "중에서",
    "즉",
    "즉시",
    "지든지",
    "지만",
    "지말고",
    "진짜로",
    "쪽으로",
    "차라리",
    "참",
    "첫번째로",
    "총적으로",
    "총적으로 보면",
    "통하여",
    "통해",
    "하",
    "하게되다",
    "하게하다",
    "하고 있다",
    "하곤하였다",
    "하기 때문에",
    "하기 위하여",
    "하기는한데",
    "하기만 하면",
    "하기보다는",
    "하기에",
    "하나",
    "하는 김에",
    "하는 편이 낫다",
    "하는것도",
    "하는바",
    "하더라도",
    "하도록하다",
    "하려고하다",
    "하마터면",
    "하면 할수록",
    "하면서",
    "하물며",
    "하여금",
    "하여야",
    "하자마자",
    "하지 않는다면",
    "하지 않도록",
    "하지마",
    "하지만",
    "한 까닭에",
    "한 이유는",
    "한 후",
    "한다면",
    "한데",
    "한마디",
    "한적이있다",
    "할 따름이다",
    "할 생각이다",
    "할 지경이다",
    "할만하다",
    "할망정",
    "할수있다",
    "할지언정",
    "함께",
    "해도된다",
    "해야한다",
    "해서는 안된다",
    "했어요",
    "향하여",
    "향해서",
    "혹시",
    "혹은",
    "혼자",
    "훨씬",
    "힘입어",
    "부",
    "개",
    "마리",
    "사본",
    "1부",
    "2부",
    "부",
    "사본 1부",
]


def extract_top_n_nouns(text: str, top_n: int = 6, min_len: int = 2) -> list:
    results = kiwi.analyze(text, top_n=1)[0][0]

    nouns = [
        token.form
        for token in results
        if token.tag.startswith("NN")
        and len(token.form) >= min_len
        and token.form not in korean_stopwords
    ]

    noun_counts = Counter(nouns)

    top_nouns = [word for word, _ in noun_counts.most_common(top_n)]

    return top_nouns


def clean_text(text: str) -> str:
    """
    Remove special characters and invisible unicode symbols from the text.
    Keeps Korean, English, digits, and whitespace only.
    """
    # Remove common special characters (except letters, digits, and whitespace)
    text = re.sub(r"[^\w\s가-힣]", "", text)

    # Remove invisible unicode characters like \ufeff, \u200b, etc.
    text = re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]", "", text)

    return text.strip()


with open(input_file, encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        combined_text = item["question"] + " " + item["answer"]
        texts.append(combined_text)
        data.append(item)

# BERTopic clustering
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
vectorizer_model = CountVectorizer(
    ngram_range=(1, 2), stop_words=korean_stopwords, min_df=2, max_df=0.9
)

topic_model = BERTopic(
    embedding_model=embedding_model,
    vectorizer_model=vectorizer_model,
    top_n_words=3,
    language="multilingual",  # support korean
)

cleaned_texts = [
    " ".join(extract_top_n_nouns(clean_text(text), top_n=20)) for text in texts
]

topics, _ = topic_model.fit_transform(cleaned_texts)

# get topic
topic_info = topic_model.get_topic_info()
topic_keywords = {}

for topic_id in topic_info["Topic"]:
    if topic_id == -1:
        continue
    words = [word for word, _ in topic_model.get_topic(topic_id)[:3]]
    topic_keywords[topic_id] = words

# add categories to original jsonl
for idx, item in enumerate(data):
    topic_id = topics[idx]
    combined_text = item["question"] + " " + item["answer"]
    top_n_nouns = extract_top_n_nouns(combined_text, top_n=6)

    # If the prefix contains [], use it as a keyword
    # ex) [네이버쇼핑] 네이버쇼핑 입점 신청은 어떻게 하나요?
    match = re.match(r"^\[([^\[\]]+)\]", combined_text)
    high_related_topic = []
    if match is not None:
        high_related_topic.append(match.group(1))

    if topic_id == -1:
        item["categories"] = high_related_topic + top_n_nouns
    else:
        item["categories"] = high_related_topic + list(
            set(topic_keywords.get(topic_id, []) + top_n_nouns[:3])
        )

# save file
with open(output_file, "w", encoding="utf-8") as f:
    for item in data:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
