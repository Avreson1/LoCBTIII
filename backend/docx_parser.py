from docx import Document
import re
from typing import List, Dict, Any

def parse_docx_test(filepath: str) -> List[Dict[str, Any]]:
    """
    Parses a docx file for questions.
    Format expectations:
    Q: Question Text
    A. Option
    B. Option
    ANSWER: X
    """
    doc = Document(filepath)
    questions = []
    current_q = None

    # Simple state machine
    # States: FIND_Q, FIND_OPTIONS, FIND_ANSWER

    text_lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    for line in text_lines:
        # Detect Question Start
        if line.startswith("Q:") or line.startswith("1.") or re.match(r'^\d+\.', line):
            # If we were building a question, save it (if incomplete, discard or log)
            if current_q and current_q.get('options') and current_q.get('correct_answer'):
                questions.append(current_q)

            # Start new question
            # Remove the prefix "Q:" or "1."
            clean_text = re.sub(r'^(Q:|Q\.|Question:|^\d+\.)\s*', '', line).strip()
            current_q = {
                "text": clean_text,
                "options": [],
                "correct_answer": None
            }
            continue

        # If we have a current question, look for options or answer
        if current_q is not None:
            # Check for Answer
            # Matches: "ANSWER: A", "Ans: B", "Key: C"
            ans_match = re.match(r'^(ANSWER|Ans|Key|Answer):\s*([A-Za-z])', line, re.IGNORECASE)
            if ans_match:
                current_q['correct_answer'] = ans_match.group(2).upper()
                # Question is complete, but we wait until next Q or end of loop to append
                # so we can catch trailing options if format is weird?
                # Actually, usually answer is last. But let's just mark it.
                questions.append(current_q)
                current_q = None # Reset
                continue

            # Check for Options
            # Matches: "A. Text", "(A) Text", "A) Text"
            opt_match = re.match(r'^(\(?([A-Za-z])[\.\)])\s*(.*)', line)
            if opt_match:
                label = opt_match.group(2).upper()
                text = opt_match.group(3).strip()
                current_q['options'].append({"label": label, "text": text})
                continue

            # If line is just text and we are in a question, maybe it's continuation of question text?
            # For simplicity, we assume single line questions for now as per manual example.

    # Append last question if valid
    if current_q and current_q.get('options') and current_q.get('correct_answer'):
        questions.append(current_q)

    return questions
