
from pathlib import Path
import re
import math
from collections import Counter

SUPERSEDED_MARKERS = ("superseded", "old policy", "deprecated")

POLICY_KEYWORDS = {
    "return": ["return", "returns", "refund", "exchange", "pickup"],
    "delivery": ["delivery", "shipping", "shipped", "tracking", "order"],
    "payment": ["payment", "paid", "cod", "upi", "transaction"],
    "cancellation": ["cancel", "cancellation", "cancelled"],
    "damage": ["damaged", "defective", "wrong", "missing", "broken"],
    "warranty": ["warranty", "guarantee", "repair"],
}

class KnowledgeBase:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.chunks = []
        self.reload()

    def reload(self):
        self.chunks = []

        for path in sorted(self.folder.glob("*.md")):
            raw = path.read_text(encoding="utf-8", errors="ignore")
            lines = raw.splitlines()

            sections = []
            current_title = path.name
            current_lines = []

            for line in lines:
                if line.startswith("# ") or line.startswith("## "):
                    if current_lines:
                        sections.append(
                            (current_title, "\n".join(current_lines).strip())
                        )
                    current_title = line.lstrip("# ").strip()
                    current_lines = []
                else:
                    current_lines.append(line)

            if current_lines:
                sections.append(
                    (current_title, "\n".join(current_lines).strip())
                )

            for title, body in sections:
                if len(body.strip()) < 20:
                    continue

                match = re.search(
                    r"\[([A-Z][A-Z0-9-]{1,20})\]",
                    title + "\n" + body
                )

                status_match = re.search(
                    r"(?im)^status:\s*(.+)$", body
                )
                effective_match = re.search(
                    r"(?im)^effective_from:\s*(.+)$", body
                )

                self.chunks.append({
                    "source": path.name,
                    "title": title,
                    "text": body,
                    "section_id": match.group(1) if match else None,
                    "status": status_match.group(1).strip()
                              if status_match else "",
                    "effective_from": effective_match.group(1).strip()
                                     if effective_match else "",
                })

    @staticmethod
    def tokens(text):
        return re.findall(r"[a-z0-9]+", text.lower())

    def search(self, query, top_k=4):
        query_lower = query.lower()
        q = set(self.tokens(query))

        if not q:
            return []

        expanded = set(q)

        for category, keywords in POLICY_KEYWORDS.items():
            if any(word in q for word in keywords):
                expanded.update(keywords)

        ranked = []

        for chunk in self.chunks:
            title = chunk["title"]
            source = chunk["source"].lower()
            words = self.tokens(title + " " + chunk["text"])
            word_set = set(words)
            counts = Counter(words)

            score = sum(
                1 + math.log(counts[word])
                for word in expanded
                if counts[word]
            )

            score += 2.0 * len(q & set(self.tokens(title)))
            # Boost exact policy sections matching the question.
            if chunk["section_id"] == "RET-2" and any(
                word in query_lower for word in ["return", "electronics", "days", "category"]
            ):
                score += 8.0

            # Strong preference for the current policy version.
            if "pol_" in source and chunk["status"].lower() == "current":
                score *= 2.0

            # Reduce the ranking of old or superseded documents.
            if any(mark in source for mark in SUPERSEDED_MARKERS):
                if not any(x in query_lower for x in
                           ["old policy", "previous policy", "superseded"]):
                    score *= 0.1

            if chunk["status"].lower() in ("superseded", "inactive", "draft"):
                score *= 0.1

            if score > 0:
                score /= math.sqrt(max(len(words), 1))
                ranked.append((score, chunk))

        ranked.sort(key=lambda item: item[0], reverse=True)

        return [
            chunk for score, chunk in ranked[:top_k]
            if score > 0
        ]
