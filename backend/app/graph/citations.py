"""Deterministic citation assembly from retrieval hits."""

from app.retrieval.retriever import RetrievalHit


def platform_display(video_label: str) -> str:
    return "YouTube (Video A)" if video_label == "A" else "Instagram (Video B)"


def assemble_citations(hits: list[RetrievalHit]) -> tuple[list[dict], str]:
    """
    Build numbered citations and an evidence block for the LLM.
    Returns (citations_json-serializable, evidence_block).
    """
    citations: list[dict] = []
    evidence_lines: list[str] = []

    for index, hit in enumerate(hits, start=1):
        cite = {
            "index": index,
            "video_label": hit.video_label,
            "video_id": hit.video_id,
            "chunk_id": hit.chunk_id,
            "chunk_index": hit.chunk_index,
            "start_time": hit.start_time,
            "end_time": hit.end_time,
            "excerpt": hit.text[:500],
            "platform": hit.platform,
            "url": hit.url,
            "title": hit.title,
            "creator": hit.creator,
            "score": hit.score,
        }
        citations.append(cite)
        label = platform_display(hit.video_label)
        evidence_lines.append(
            f"[{index}] {label} | {hit.start_time:.1f}s–{hit.end_time:.1f}s | "
            f"chunk_id={hit.chunk_id}\n{hit.text}"
        )

    if not evidence_lines:
        evidence_block = "No transcript evidence retrieved for this query."
    else:
        evidence_block = "\n\n".join(evidence_lines)

    return citations, evidence_block


def build_prompts(
    comparison_facts: str,
    evidence_block: str,
    user_message: str,
) -> tuple[str, str]:
    system_prompt = """You are HookLens AI, a creator intelligence analyst comparing Video A (YouTube) vs Video B (Instagram Reel).

Rules:
- Answer ONLY using the comparison facts and numbered transcript evidence below.
- Cite evidence with bracket numbers matching the excerpts, e.g. [1], [2].
- For each claim, state whether it refers to Video A (YouTube) or Video B (Instagram).
- Include timestamps when citing transcript evidence.
- If evidence is insufficient, say so explicitly. Never invent metrics, quotes, or timestamps.
- For follow-up questions, use conversation history plus the evidence provided for this turn."""

    user_prompt = f"""{comparison_facts}

=== Retrieved transcript evidence ===
{evidence_block}

=== User question ===
{user_message}

Provide a clear, evidence-backed answer with citations like [1], [2]."""

    return system_prompt, user_prompt
