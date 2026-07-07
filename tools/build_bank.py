from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pdfplumber
from PIL import Image


PDF_PATH = Path(r"C:\CB\4-My work\424冷阴极X射线源\5其他\省辐射安全考试\X射线探伤.pdf")
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
QUESTION_DIR = ROOT / "assets" / "questions"

SCALE = 2.5
MARGIN_X = 22
MARGIN_TOP = 2
MARGIN_BOTTOM = 1

SECTIONS = [
    {
        "key": "basic",
        "name": "电离辐射安全与防护基础",
        "answer_heading": "一、电离辐射安全与防护基础答案",
        "page_start": 3,
        "page_end": 23,
        "single_end": 124,
        "multi_start": 125,
        "multi_end": 169,
    },
    {
        "key": "law",
        "name": "核技术利用辐射安全法律法规",
        "answer_heading": "二、核技术利用辐射安全法律法规答案",
        "page_start": 24,
        "page_end": 38,
        "single_end": 84,
        "multi_start": 85,
        "multi_end": 131,
    },
    {
        "key": "practice",
        "name": "专业实务",
        "answer_heading": "三、专业实务答案",
        "page_start": 39,
        "page_end": 64,
        "single_end": 59,
        "multi_start": 60,
        "multi_end": 107,
    },
]


@dataclass
class Marker:
    qid: int
    page_index: int
    x0: float
    top: float
    text: str


def question_kind(section: dict, qid: int) -> str:
    if qid <= section["single_end"]:
        return "single"
    return "multiple"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\u3000", " ")).strip()


def parse_answer_pairs(text: str) -> dict[int, list[str]]:
    pairs = re.findall(r"(\d{1,3})\.([A-E](?:,[A-E])*)", text)
    return {int(raw_id): raw_answer.split(",") for raw_id, raw_answer in pairs}


def parse_answers(pdf: pdfplumber.PDF) -> dict[str, dict[int, list[str]]]:
    answer_text = "\n".join((pdf.pages[i].extract_text() or "") for i in range(65, len(pdf.pages)))
    answers: dict[str, dict[int, list[str]]] = {}
    for index, section in enumerate(SECTIONS):
        start = answer_text.find(section["answer_heading"])
        if start == -1:
            answers[section["key"]] = {}
            continue
        next_starts = [
            answer_text.find(next_section["answer_heading"], start + 1)
            for next_section in SECTIONS[index + 1 :]
            if answer_text.find(next_section["answer_heading"], start + 1) != -1
        ]
        end = min(next_starts) if next_starts else len(answer_text)
        answers[section["key"]] = parse_answer_pairs(answer_text[start:end])
    return answers


def marker_candidates(words: Iterable[dict], page_index: int) -> list[Marker]:
    markers: list[Marker] = []
    for word in words:
        text = str(word.get("text", ""))
        match = re.match(r"^(\d{1,3})[、.．]", text)
        if not match:
            continue
        qid = int(match.group(1))
        # Avoid answer pages and table of contents/page numbers. Real question markers sit near the left text column.
        if not (1 <= qid <= 450):
            continue
        if word["x0"] > 120 or word["top"] < 50:
            continue
        markers.append(Marker(qid=qid, page_index=page_index, x0=word["x0"], top=word["top"], text=text))
    return markers


def detect_markers(pdf: pdfplumber.PDF, section: dict) -> list[Marker]:
    markers: list[Marker] = []
    for page_index in range(section["page_start"], section["page_end"] + 1):
        page = pdf.pages[page_index]
        words = page.extract_words(x_tolerance=2, y_tolerance=3, keep_blank_chars=False)
        markers.extend(marker_candidates(words, page_index))
    unique: dict[int, Marker] = {}
    for marker in sorted(markers, key=lambda item: (item.qid, item.page_index, item.top)):
        unique.setdefault(marker.qid, marker)
    return [unique[qid] for qid in sorted(unique)]


def crop_box_for(marker: Marker, next_marker: Marker | None, page_width: float, page_height: float) -> tuple[float, float, float, float]:
    left = max(0, marker.x0 - MARGIN_X)
    top = max(0, marker.top - MARGIN_TOP)
    right = page_width - 28
    if next_marker and next_marker.page_index == marker.page_index:
        bottom = max(top + 45, next_marker.top - MARGIN_BOTTOM)
    else:
        bottom = page_height - 40
    return left, top, right, min(page_height, bottom)


def crop_question_images(pdf: pdfplumber.PDF, all_markers: dict[str, list[Marker]], all_answers: dict[str, dict[int, list[str]]]) -> tuple[list[dict], list[dict]]:
    QUESTION_DIR.mkdir(parents=True, exist_ok=True)
    for old_image in QUESTION_DIR.glob("*.jpg"):
        old_image.unlink()
    questions: list[dict] = []
    review: list[dict] = []

    for section in SECTIONS:
        key = section["key"]
        answers = all_answers.get(key, {})
        markers = all_markers.get(key, [])
        marker_by_id = {marker.qid: marker for marker in markers}
        for qid in sorted(answers):
            marker = marker_by_id.get(qid)
            if not marker:
                review.append({"id": f"{key}-{qid:03d}", "section": section["name"], "issue": "未定位到题号，未生成截图", "answer": answers[qid]})
                continue

            next_marker = marker_by_id.get(qid + 1)
            page = pdf.pages[marker.page_index]
            box = crop_box_for(marker, next_marker, page.width, page.height)
            cropped = page.crop(box)
            image = cropped.to_image(resolution=int(72 * SCALE), antialias=True).original.convert("RGB")

            image_name = f"{key}_{qid:03d}.jpg"
            image_path = QUESTION_DIR / image_name
            image.save(image_path, quality=88, optimize=True)

            options_count = max((ord(answer) - ord("A") + 1 for answer in answers[qid]), default=4)
            kind = question_kind(section, qid)
            questions.append(
                {
                    "id": f"{key}-{qid:03d}",
                    "number": qid,
                    "section": section["name"],
                    "sectionKey": key,
                    "type": kind,
                    "answer": answers[qid],
                    "image": f"assets/questions/{image_name}",
                    "page": marker.page_index + 1,
                    "options": [chr(ord("A") + i) for i in range(max(4, options_count))],
                }
            )

            if (box[3] - box[1]) < 32:
                review.append({"id": f"{key}-{qid:03d}", "section": section["name"], "issue": "截图高度偏小，请人工复核", "page": marker.page_index + 1})

    return questions, review


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with pdfplumber.open(PDF_PATH) as pdf:
        answers = parse_answers(pdf)
        markers = {section["key"]: detect_markers(pdf, section) for section in SECTIONS}
        questions, review = crop_question_images(pdf, markers, answers)

    ids = [item["id"] for item in questions]
    expected_by_section = {
        section["key"]: set(range(1, section["multi_end"] + 1))
        for section in SECTIONS
    }
    missing_answer_ids = [
        f"{key}-{qid:03d}"
        for key, expected in expected_by_section.items()
        for qid in sorted(expected - set(answers.get(key, {})))
    ]
    image_id_set = set(ids)
    missing_image_ids = [
        f"{key}-{qid:03d}"
        for key, answer_map in answers.items()
        for qid in sorted(answer_map)
        if f"{key}-{qid:03d}" not in image_id_set
    ]
    duplicate_ids = sorted({qid for qid in ids if ids.count(qid) > 1})

    meta = {
        "title": "X射线探伤辐射安全考核题库",
        "source": "X射线探伤.pdf",
        "questionMode": "PDF截图题面",
        "answerSource": "第四部分答案",
        "totalAnswers": sum(len(answer_map) for answer_map in answers.values()),
        "totalQuestions": len(questions),
        "sections": [
            {"key": item["key"], "name": item["name"], "singleEnd": item["single_end"], "multiStart": item["multi_start"], "multiEnd": item["multi_end"]}
            for item in SECTIONS
        ],
    }
    checks = {
        "missingAnswerIds": missing_answer_ids,
        "missingImageIds": missing_image_ids,
        "duplicateIds": duplicate_ids,
        "review": review,
    }

    (DATA_DIR / "questions.json").write_text(json.dumps({"meta": meta, "questions": questions}, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "build-checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({**meta, **checks}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
