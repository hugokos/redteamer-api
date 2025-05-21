import json
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB

class KGLoader:
    def __init__(self, path: str):
        self.entries = json.load(open(path, "r"))
        self.graph   = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        for e in self.entries:
            tone = e["tone"]
            self.graph.add_node(tone, category="tone",
                                description=e["description"],
                                examples=e["example_phrases"])
            for r in e["risks"]:
                self.graph.add_node(r, category="risk")
                self.graph.add_edge(tone, r)

    def get_risks(self, tone: str):
        if tone not in self.graph:
            return []
        return [n for n in nx.descendants(self.graph, tone)
                if self.graph.nodes[n].get("category") == "risk"]

class Evaluator:
    FEEDBACK = {
        "escalation":    "This response risks escalating the situation.",
        "customer_loss": "This tone may drive the customer away.",
        "off_brand":     "This tone may feel off-brand for a support scenario."
    }

    def __init__(self, kg_path: str, thresh: float = 0.02):
        self.kg    = KGLoader(kg_path)
        self.thresh = thresh
        self.tones  = [e["tone"] for e in self.kg.entries]
        texts, labels = [], []
        for e in self.kg.entries:
            tone = e["tone"]
            for ex in e["example_phrases"]:
                texts.append(ex)
                labels.append([1 if tone == t else 0 for t in self.tones])

        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1)
        X = self.vectorizer.fit_transform(texts)
        self.clf = OneVsRestClassifier(MultinomialNB()).fit(X, labels)

    def detect_tones(self, text: str):
        txt = text.lower()
        tags = []
        for e in self.kg.entries:
            tone = e["tone"]
            for ex in e["example_phrases"]:
                if ex.lower() in txt:
                    tags.append(tone)
                    break
        remaining = [t for t in self.tones if t not in tags]
        if remaining:
            Xv = self.vectorizer.transform([text])
            probs = self.clf.predict_proba(Xv)[0]
            for tone, p in zip(self.tones, probs):
                if tone in remaining and p >= self.thresh:
                    tags.append(tone)
        return tags

    def evaluate(self, user_text: str, bot_text: str):
        tags = self.detect_tones(bot_text)
        flags, reasoning = set(), []
        for t in tags:
            for r in self.kg.get_risks(t):
                flags.add(r)
                reasoning.append(f"{t} → {r}")
        score = len(flags)
        feedback = " ".join(self.FEEDBACK.get(r, f"Risk: {r}") for r in flags) \
                   or "No major tone issues detected."
        return {
            "score":     score,
            "tone_tags": tags,
            "flags":     sorted(flags),
            "reasoning": reasoning,
            "feedback":  feedback
        }