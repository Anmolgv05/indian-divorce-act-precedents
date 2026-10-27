"""
Task 7: Gradio Web UI for Section 10 Indian Divorce Act Precedent Search.
- Pure retrieval over indexed judgments (No LLM calls).
- Scope notice and out-of-scope warnings for adjacent statutes.
- Result cards with Indian Kanoon links, rule badges, and argument/reasoning segments.
- Outcome statistics and transparent rule caveats.
"""

import os
import sys
import html
import gradio as gr

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.search import search, stats, out_of_scope_notice


GROUND_CHOICES = [
    "All",
    "Adultery",
    "Cruelty",
    "Desertion",
    "Nullity (s.19)",
    "Mutual consent (s.10A)",
    "Non-consummation",
    "Unsound mind",
    "Conversion",
    "Procedural",
    "Constitutional validity"
]

GROUND_LOOKUP = {
    "All": None,
    "Adultery": "adultery",
    "Cruelty": "cruelty",
    "Desertion": "desertion",
    "Nullity (s.19)": "nullity_sec19",
    "Mutual consent (s.10A)": "mutual_consent_10A",
    "Non-consummation": "non_consummation",
    "Unsound mind": "unsound_mind",
    "Conversion": "conversion",
    "Procedural": "procedural",
    "Constitutional validity": "constitutional_validity"
}

HUMAN_GROUND_DISPLAY = {
    "adultery": "Adultery",
    "cruelty": "Cruelty",
    "desertion": "Desertion",
    "nullity_sec19": "Nullity (s.19)",
    "mutual_consent_10A": "Mutual consent (s.10A)",
    "non_consummation": "Non-consummation",
    "unsound_mind": "Unsound mind",
    "conversion": "Conversion",
    "procedural": "Procedural",
    "constitutional_validity": "Constitutional validity",
    "unclear": "not determined"
}


def format_badge(label: str, text: str, color: str = "#4b5563") -> str:
    clean_text = "not determined" if str(text).lower() == "unclear" else str(text)
    return (
        f'<span style="display:inline-block; padding:2px 8px; margin:2px 4px 2px 0; '
        f'background-color:{color}; color:#ffffff; border-radius:4px; font-size:12px; font-weight:500;">'
        f'{html.escape(label)}: {html.escape(clean_text)}</span>'
    )


def format_results_html(results: list[dict]) -> str:
    if not results:
        return (
            '<div style="padding:20px; text-align:center; color:#6b7280; font-style:italic;">'
            'No matching judgments found for this query and filter criteria.'
            '</div>'
        )

    cards = []
    for idx, r in enumerate(results, 1):
        did = html.escape(str(r.get("doc_id", "")))
        title = html.escape(str(r.get("title", "Untitled Judgment")))
        url = html.escape(str(r.get("url", f"https://indiankanoon.org/doc/{did}/")))
        year_str = str(r.get("year")) if r.get("year") is not None else "n/a"
        court = html.escape(str(r.get("court", "Unknown Court")))

        # Map labels with "not determined" for unclear
        disp = r.get("disposal", "unclear")
        diss = r.get("marriage_dissolved", "unclear")
        relief = r.get("relief", "unclear")
        raw_ground = r.get("primary_ground", "unclear")
        ground_display = HUMAN_GROUND_DISPLAY.get(raw_ground, raw_ground)

        # Neutral color coding for badges (avoiding green/red value judgments)
        diss_color = "#334155" if diss == "yes" else "#475569" if diss == "no" else "#64748b"
        disp_color = "#334155" if disp in ("allowed", "confirmed") else "#475569" if disp in ("dismissed", "not_confirmed") else "#64748b"

        badges = [
            format_badge("Year", year_str, "#374151"),
            format_badge("Court", court, "#374151"),
            format_badge("Ground", ground_display, "#0369a1"),
            format_badge("Disposal", disp, disp_color),
            format_badge("Dissolved", diss, diss_color),
            format_badge("Relief", relief, "#475569"),
        ]

        if r.get("non_merits"):
            badges.append(format_badge("Tag", "non-merits (transfer/procedural)", "#9333ea"))
        if r.get("possible_duplicate_of"):
            dup_id = html.escape(str(r.get("possible_duplicate_of")))
            badges.append(format_badge("Duplicate", f"Pair of {dup_id}", "#d97706"))

        badges_html = "".join(badges)

        # Best chunk preview
        best_chunk = r.get("best_chunk", {})
        best_text = html.escape(best_chunk.get("text", "")).replace("\n", "<br>")
        best_type = html.escape(str(best_chunk.get("segment_type", "passage")))
        score_val = r.get("score", 0.0)

        # Expandable role segments
        pet_arg = r.get("petitioner_argument")
        resp_arg = r.get("respondent_argument")
        reasoning = r.get("reasoning")

        details_blocks = []
        if pet_arg and pet_arg.get("text"):
            p_text = html.escape(pet_arg["text"]).replace("\n", "<br>")
            details_blocks.append(
                f'<details style="margin:6px 0; padding:6px 10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:4px;">'
                f'<summary style="font-weight:600; cursor:pointer; color:#0f172a;">Petitioner Arguments</summary>'
                f'<div style="margin-top:6px; font-size:13px; color:#334155; line-height:1.5;">{p_text}</div>'
                f'</details>'
            )

        if resp_arg and resp_arg.get("text"):
            r_text = html.escape(resp_arg["text"]).replace("\n", "<br>")
            details_blocks.append(
                f'<details style="margin:6px 0; padding:6px 10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:4px;">'
                f'<summary style="font-weight:600; cursor:pointer; color:#0f172a;">Respondent Arguments</summary>'
                f'<div style="margin-top:6px; font-size:13px; color:#334155; line-height:1.5;">{r_text}</div>'
                f'</details>'
            )

        if reasoning and reasoning.get("text"):
            re_text = html.escape(reasoning["text"]).replace("\n", "<br>")
            details_blocks.append(
                f'<details style="margin:6px 0; padding:6px 10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:4px;">'
                f'<summary style="font-weight:600; cursor:pointer; color:#0f172a;">Court\'s Reasoning</summary>'
                f'<div style="margin-top:6px; font-size:13px; color:#334155; line-height:1.5;">{re_text}</div>'
                f'</details>'
            )

        details_html = "".join(details_blocks)

        card_html = f"""
        <div style="margin-bottom:20px; padding:16px 20px; border:1px solid #e2e8f0; border-radius:8px; background:#ffffff; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px;">
                <div style="font-size:17px; font-weight:700;">
                    <span style="color:#64748b; margin-right:6px;">#{idx}</span>
                    <a href="{url}" target="_blank" rel="noopener noreferrer" style="color:#1d4ed8; text-decoration:none;">
                        {title}
                    </a>
                </div>
                <div style="font-size:12px; color:#64748b; font-family:monospace;">
                    Match Score: {score_val:.4f}
                </div>
            </div>
            <div style="margin-bottom:12px;">
                {badges_html}
            </div>
            <div style="padding:10px 14px; background:#f1f5f9; border-left:4px solid #3b82f6; border-radius:4px; font-size:13px; line-height:1.6; color:#1e293b; margin-bottom:10px;">
                <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:#64748b; margin-bottom:4px;">
                    Best Matching Passage ({best_type}):
                </div>
                {best_text}
            </div>
            {details_html}
        </div>
        """
        cards.append(card_html)

    return "\n".join(cards)


def run_ui_search(
    query: str,
    ground_filter: str,
    year_min: int,
    year_max: int,
    include_non_merits: bool,
    show_duplicates: bool,
    top_k: int
):
    clean_query = query.strip()
    if not clean_query:
        return "", "", ""

    target_ground = GROUND_LOOKUP.get(ground_filter, None)
    year_range = (int(year_min), int(year_max))

    results = search(
        query=clean_query,
        top_k=int(top_k),
        ground=target_ground,
        year_range=year_range,
        include_non_merits=bool(include_non_merits),
        include_duplicates=bool(show_duplicates),
        mode="hybrid"
    )

    st = stats(results, query=clean_query)

    # 1. Scope and confidence notices
    notice_banners = []
    scope_warn = st.get("out_of_scope_notice")
    if scope_warn:
        notice_banners.append(
            f'<div style="padding:12px 16px; margin-bottom:12px; background:#fef3c7; border:1px solid #f59e0b; border-radius:6px; color:#92400e; font-size:14px; line-height:1.5;">'
            f'<strong>⚠️ Statute Notice:</strong> {html.escape(scope_warn)}'
            f'</div>'
        )

    if st.get("low_confidence"):
        top_sc = getattr(results, "top_score", (results[0]["score"] if results else 0.0))
        notice_banners.append(
            f'<div style="padding:12px 16px; margin-bottom:12px; background:#fee2e2; border:1px solid #ef4444; border-radius:6px; color:#991b1b; font-size:14px; line-height:1.5;">'
            f'<strong>⚠️ Low Confidence Warning:</strong> Top match score is {top_sc:.4f}. '
            f'Your query may be out-of-corpus, ambiguous, or not centered on Christian divorce jurisprudence.'
            f'</div>'
        )

    banners_html = "\n".join(notice_banners)

    # 2. Stats summary line
    summary_text = st.get("summary", "")
    stats_html = (
        f'<div style="padding:12px 16px; margin-bottom:16px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; color:#1e40af; font-size:14px; font-weight:500;">'
        f'📊 {html.escape(summary_text)}'
        f'</div>'
    )

    # 3. Formatted result cards
    results_html = format_results_html(results)

    return banners_html, stats_html, results_html


def build_app():
    custom_css = """
    .gradio-container { max-width: 1050px !important; margin: 0 auto !important; }
    """

    with gr.Blocks(title="Section 10 Indian Divorce Act Precedent Search", css=custom_css) as demo:
        gr.Markdown(
            """
            # Section 10 Indian Divorce Act Precedent Search
            > **Scope Notice:** Only Indian Divorce Act (Christian marriages) judgments. Similar past cases, not predictions, not legal advice.
            """
        )

        with gr.Row():
            with gr.Column(scale=9):
                query_box = gr.Textbox(
                    label="Search Query",
                    placeholder="Enter factual scenario, grounds, or legal points (e.g. husband alleges wife deserted him for three years)",
                    lines=2,
                    show_label=False
                )
            with gr.Column(scale=1):
                search_btn = gr.Button("Search", variant="primary", scale=1)

        with gr.Accordion("Filters and Advanced Options", open=False):
            with gr.Row():
                ground_dropdown = gr.Dropdown(
                    label="Filter by Primary Ground",
                    choices=GROUND_CHOICES,
                    value="All"
                )
                top_k_slider = gr.Slider(
                    label="Results to Retrieve (Top K)",
                    minimum=1,
                    maximum=20,
                    value=5,
                    step=1
                )

            with gr.Row():
                year_slider = gr.Slider(
                    label="Earliest Year (Min: 1869)",
                    minimum=1869,
                    maximum=2026,
                    value=1869,
                    step=1
                )
                year_max_slider = gr.Slider(
                    label="Latest Year (Max: 2026)",
                    minimum=1869,
                    maximum=2026,
                    value=2026,
                    step=1
                )

            with gr.Row():
                non_merits_check = gr.Checkbox(
                    label="Include non-merits cases (e.g. transfer petitions)",
                    value=False
                )
                duplicates_check = gr.Checkbox(
                    label="Show possible duplicate records",
                    value=False
                )

        gr.Examples(
            examples=[
                ["husband alleges wife deserted him for three years without reasonable cause"],
                ["wife seeks divorce on ground of husband living in adultery"],
                ["husband treated wife with physical and mental cruelty making cohabitation impossible"],
                ["marriage not consummated due to respondent wilful refusal"],
                ["joint petition under section 10A for dissolution of marriage by mutual consent"],
                ["restitution of conjugal rights under section 32 without reasonable excuse"],
                ["petition for declaration of nullity of marriage under section 19"],
                ["divorce under Hindu Marriage Act section 13 cruelty"],  # Out-of-scope trigger demo
            ],
            inputs=[query_box],
            label="Sample Queries"
        )

        notices_output = gr.HTML()
        stats_output = gr.HTML()
        results_output = gr.HTML()

        search_btn.click(
            fn=run_ui_search,
            inputs=[
                query_box,
                ground_dropdown,
                year_slider,
                year_max_slider,
                non_merits_check,
                duplicates_check,
                top_k_slider
            ],
            outputs=[notices_output, stats_output, results_output]
        )

        query_box.submit(
            fn=run_ui_search,
            inputs=[
                query_box,
                ground_dropdown,
                year_slider,
                year_max_slider,
                non_merits_check,
                duplicates_check,
                top_k_slider
            ],
            outputs=[notices_output, stats_output, results_output]
        )

        gr.Markdown(
            """
            ---
            <div style="text-align: center; color: #64748b; font-size: 13px;">
                ⚠️ <strong>Disclaimer:</strong> All classifications (grounds, disposal, outcome) are generated by automated rule-based analysis of judicial tails and may contain errors. This tool is designed strictly for legal research and case law exploration, not for outcome prediction or legal advice.
            </div>
            """
        )

    return demo


if __name__ == "__main__":
    demo = build_app()
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
