from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from snapshot_operations import download_snapshot, poll_snapshot_status
from openai import OpenAI
import json
from platforms_activities import summarize_platform_activity
import time

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


# def _make_api_request(url, **kwargs):
#     api_key = os.getenv("BRIGHTDATA_API_KEY")
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json",
#     }
#     print("prepared_urls nnamNA", url)
#     try:
#         response = requests.post(url, headers=headers, **kwargs)
#         response.raise_for_status()
        
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"API request failed: {e}")
#         return None
#     except Exception as e:
#         print(f"Unknown error: {e}")
#         return None
def _make_api_request(url, **kwargs):
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    attempt = 0  # kitni dafa try ho chuka hai

    while True:  # jab tak success na ho jaye
        attempt += 1
        print(f"[TRY {attempt}] prepared_urls nnamNA {url}")

        try:
            response = requests.post(url, headers=headers, **kwargs)
            response.raise_for_status()  # 4xx / 5xx pe exception throw karega

            # yahan pohanch gaye matlab success ho gaya
            print(f"[SUCCESS] Status: {response.status_code}")
            return response.json()

        except requests.exceptions.RequestException as e:
            # network error, timeout, 5xx, etc.
            wait_seconds = min(60, 2 ** attempt)  # 2, 4, 8, 16... max 60 sec
            print(f"[ERROR] API request failed: {e}")
            print(f"[INFO] {wait_seconds} seconds baad dobara try kar raha hoon...")
            time.sleep(wait_seconds)

        except Exception as e:
            # koi unexpected error
            wait_seconds = min(60, 2 ** attempt)
            print(f"[UNKNOWN ERROR] {e}")
            print(f"[INFO] {wait_seconds} seconds baad dobara try kar raha hoon...")
            time.sleep(wait_seconds)


def _trigger_and_download_snapshot(trigger_url, params, data, operation_name="operation"):
    trigger_result = _make_api_request(trigger_url, params=params, json=data)
    if not trigger_result:
        return None
    
    snapshot_id = trigger_result.get("snapshot_id")
    print(snapshot_id)
    if not snapshot_id:
        return None

    if not poll_snapshot_status(snapshot_id):
        return None
    raw_data = download_snapshot(snapshot_id)
    return raw_data





def serp_search(query, engine="google"):
    if engine == "google":
        base_url = "https://www.google.com/search"
    elif engine == "bing":
        base_url = "https://www.bing.com/search"
    else:
        raise ValueError(f"Unknown engine {engine}")

    url = "https://api.brightdata.com/request"

    payload = {
        "zone": "ai_agent",
        "url": f"{base_url}?q={quote_plus(query)}&brd_json=1",
        "format": "raw"
    }

    full_response = _make_api_request(url, json=payload)
    if not full_response:
        return None

    organic_results = full_response.get("organic", [])
    extracted_data = [{"title": item.get("title"), "description": item.get("description")} for item in organic_results]
    # extracted_data = {
    #     "knowledge": full_response.get("knowledge", {}),
    #     "organic": full_response.get("organic", []),
    # }
    return extracted_data

def reddit_comment_retrieval(urls, days_back=10, load_all_replies=False, comment_limit=5):
    if not urls:
        return None

    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
    params = {
        "dataset_id": "gd_lvzdpsdlw09j6t702",
        "include_errors": "true"
    }

    data = [
        {
            "url": url,
            "days_back": days_back,
            "load_all_replies": load_all_replies,
            "comment_limit": comment_limit
        }
        for url in urls
    ]

    raw_data = _trigger_and_download_snapshot(
        trigger_url, params, data, operation_name="reddit comments"
    )
    if not raw_data:
        return None

    parsed_comments = []
    for comment in raw_data:
        parsed_comment = {
            "comment_text": comment.get("comment"),
        }
        parsed_comments.append(parsed_comment)

    return parsed_comments


#******************** YouTube*************************
def youtube_post_retrieval(urls, num_of_comments=5, sort_by="Newest first"):
    if not urls:
        return None

    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
  
    params = {
        "dataset_id": "gd_lk9q0ew71spt1mxywf",
        "include_errors": "true"
    }

    data = [
        {
            "url": url,
            "num_of_comments":num_of_comments,
            "sort_by": sort_by
        }
        for url in urls
    ]

    raw_data = _trigger_and_download_snapshot(
        trigger_url, params, data, operation_name="youtube comments"
    )
    if not raw_data:
        return None

    parsed_comments = []
    for comment in raw_data:
        parsed_comment = {
            "comment_text": comment.get("comment_text")
        }
        parsed_comments.append(parsed_comment)

    return parsed_comments

#******************** YouTube end*************************

#******************** Tiktok  *************************

def tiktok_post_retrieval(urls):
    if not urls:
        return None

    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
  
    params = {
        "dataset_id": "gd_lkf2st302ap89utw5k",
        "include_errors": "true"
    }

    data = [
        {
            "url": url,
        }
        for url in urls
    ]

    raw_data = _trigger_and_download_snapshot(
        trigger_url, params, data, operation_name="tiktok comments"
    )
    if not raw_data:
        return None

    parsed_comments = []
    for comment in raw_data:
        parsed_comment = {
            "comment_text": comment.get("comment_text")
        }
        parsed_comments.append(parsed_comment)

    return parsed_comments

#******************** Tiktok End*************************


#******************** Instagram  *************************

def instagram_comments_retrieval(urls):
    if not urls:
        return None

    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
  
    params = {
        "dataset_id": "gd_ltppn085pokosxh13",
        "include_errors": "true"
    }

    data = [
        {
            "url": url,
        }
        for url in urls
    ]

    raw_data = _trigger_and_download_snapshot(
        trigger_url, params, data, operation_name="instagram comments"
    )
    if not raw_data:
        return None

    parsed_comments = []
    for comment in raw_data:
        parsed_comment = {
            "comment_text": comment.get("comment")
        }
        parsed_comments.append(parsed_comment)

    return parsed_comments

#******************** Instagram End*************************


#******************** Facebook  *************************

def facebook_comments_retrieval(urls,get_all_replies=False,limit_records=5, comments_sort="Most relevant"):
    if not urls:
        return None

    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
  
    params = {
        "dataset_id": "gd_lkay758p1eanlolqw8",
        "include_errors": "true"

    }

    data = [
        {
            "url": url,
            "get_all_replies":get_all_replies,
            "limit_records":limit_records, 
            "comments_sort": comments_sort
        }
        for url in urls
    ]

    raw_data = _trigger_and_download_snapshot(
        trigger_url, params, data, operation_name="facebook comments"
    )
    if not raw_data:
        return None

    parsed_comments = []
    for comment in raw_data:
        parsed_comment = {
            "comment_text": comment.get("comment_text")
        }
        parsed_comments.append(parsed_comment)

    return parsed_comments

#******************** Facebook End*************************

#********************  X  *************************

def x_comments_retrieval(urls):
    if not urls:
        return None

    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
  
    params = {
        "dataset_id": "gd_lwxkxvnf1cynvib9co",
        "include_errors": "true"
    }

    data = [
        {
            "url": url,
        }
        for url in urls
    ]

    raw_data = _trigger_and_download_snapshot(
        trigger_url, params, data, operation_name="x comments"
    )
    if not raw_data:
        return None

    parsed_comments = []
    for comment in raw_data:
        parsed_comment = {
            "comment_text": comment.get("description")
        }
        parsed_comments.append(parsed_comment)

    return parsed_comments

#******************** X End  *************************


#********************  LinkedIn  *************************

def linkedin_comments_retrieval(urls):
    if not urls:
        return None

    trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
  
    params = {
        "dataset_id": "gd_lyy3tktm25m4avu764",
        "include_errors": "true"
    }

    data = [
        {
            "url": url,
        }
        for url in urls
    ]

    raw_data = _trigger_and_download_snapshot(
        trigger_url, params, data, operation_name="linkedin comments"
    )
    if not raw_data:
        return None

    parsed_comments = []
    for comment in raw_data:
        top_comments = comment.get("top_visible_comments") or []
        extracted_comments = [c.get("comment") for c in top_comments if isinstance(c, dict)]
        parsed_comment = {
            "post_text": comment.get("post_text"),
            "comment_text":extracted_comments
        }
        parsed_comments.append(parsed_comment)

    return parsed_comments

#******************** LinkedIn End  *************************

def converstional_stats(social_urls, comments_json ):
    pass

# def results_curation(social_urls,comments_json,user_query):

#     stats = summarize_platform_activity(social_urls, comments_json)

#     system_prompt = """
#         You are an expert social listening and opinion-mining analyst. Analyze user-generated text across platforms.
#         Provide an overall narrative report (no per-platform tables, no JSON), citing platform names after quotes.
#         Use only the provided data; avoid hallucinations. Keep quotes ≤ 30 words with platform names. Integer
#         sentiment percentages must sum to ~100. Include prioritized future-plan recommendations with concrete
#         actions and experiment ideas.
#         """

#     report_prompt = f"""
#         USER QUERY
#         {user_query}

#         INPUT DATA
#         {json.dumps(comments_json, indent=2, ensure_ascii=False)}

#         DELIVERABLE — Write a clear, concise narrative report with these sections (no JSON):

#         1) Executive Summary
#         2) Sentiment Snapshot (Overall) — Positive % / Negative % / Neutral %; 5–12 short quotes with platforms
#         3) Key Opinion Themes (Overall) — 3–7 themes with summaries + quotes (with platforms)
#         4) Opinion Polls   
#         - **generate 3–5 poll questions** inferred from debates, disagreements, or strong opinion clusters.  
#         - For each poll:
#             • Question (concise, neutral wording)  
#             • 2–4 answer options with supporting quotes + platform reference
#             • **Estimated Audience Split:** use realistic inferred percentages (total ≈100%) based on how frequently or strongly each opinion appears in the data. 
#             • One-sentence rationale: why this poll would be valuable for decision-making.
#         5) Crisis Detection & Brand Monitoring — severity, confidence, evidence quotes (with platforms), actions
#         6) Critical Points & Future Plan Recommendations — 5–12 prioritized, evidence-backed points with:
#         - Priority (P0/P1/P2), Impact (high/med/low), Effort (high/med/low)
#         - Evidence quote(s) with platform
#         - Specific recommended actions
#         7) Data Quality & Gaps — totals after dedup, removed empty/null, languages, off-topic notes, limitations
#     """

#     completion = client.chat.completions.create(
#         model="gpt-5-2025-08-07", 
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": report_prompt}
#         ]
#     )

#     report_text = completion.choices[0].message.content
#     conversation_references = f"\n\n---\n### Conversation References\n{json.dumps(social_urls, indent=2, ensure_ascii=False)}"
   
#     return report_text + conversation_references

def results_curation(social_urls, comments_json, user_query):
    stats_text = summarize_platform_activity(social_urls, comments_json)

    system_prompt = """
        You are an expert social listening and opinion-mining analyst.

        Goal: Produce a short, decision-ready report that answers the user query using ONLY the provided data (comments_json + stats_text).
        - Focus on opinions, rationales, trade-offs, and clear conclusions.
        - Be concise, direct, and business-oriented.
        - No speculation beyond the provided data.
        - Use simple language, short paragraphs, and avoid repeating the query.
        - Keep all quotes ≤ 30 words and tag each with its platform.
            """.strip()

    report_prompt = f"""
        USER QUERY
        {user_query}

        INPUT DATA — COMMENTS JSON
        {json.dumps(comments_json, indent=2, ensure_ascii=False)}

        INPUT DATA — PLATFORM STATS (raw string; authoritative)
        {stats_text}

        INPUT DATA — CONVERSATION REFERENCES (URLs)
        {json.dumps(social_urls, indent=2, ensure_ascii=False)}

        DELIVERABLE
        Write a concise narrative report with the following sections, in order, with headings only (no JSON in main body):

        1) User Query  
        2) Executive Summary  
        Write one short paragraph (four to six sentences). Clearly state the main answer to the query, the dominant direction of opinion, and the key reasons. No bullet points here, only a compact paragraph.

        3) Opinion Results — Question-Style Dominant Findings  
        This section must be structured as three to four question-style subheadings that summarize the main opinion patterns, similar in style to:

        ## ❌ Why BYD Is Not Better Than Tesla

        Under each question-style heading, explain the underlying reasons with numbered subheadings and short paragraphs. Each question block should look like the example below: a clear question-type title, followed by two to four numbered reasons (1., 2., 3., etc.) with a few sentences each. In those sentences, explain what people are saying and why, and weave in one or two short quotes with platform tags (each quote must be 30 words or fewer).

        Use this as a style and structure example only (do not reuse this content or these brands):

        ## ❌ Why BYD Is Not Better Than Tesla

        ### 1. *Poor Sales and After-Sales Experience*
        - BYD is repeatedly criticized for untrained or indifferent showroom staff, long repair wait times, and lack of customer support.
        - Quotes like “repairs can take up to 4 months” and “sales exp was such a turnoff that I bought another brand instead” reflect deep frustration.

        ### 2. *Tesla Wins on Software, UX, and Charging*
        - Tesla’s integrated software, refined user interface, and superior charging infrastructure are consistently praised.
        - Comments like “Model Y anytime over any BYD” and “software in Tesla is much better” show Tesla’s edge in tech and usability.

        ### 3. *Tesla Is Perceived as the “Safer” Bet*
        - Tesla is seen as more polished, reliable, and future-proof—especially for first-time EV buyers.
        - The brand’s narrative strength and owner endorsements reinforce trust, while BYD’s value is often overshadowed by service concerns.

        End of example.

        In your actual output, create three to four similar question-style headings that reflect the dominant opinion frames found in the data. Each question should clearly express a directional conclusion (for example, why one option is preferred, why something is not good enough, why people are hesitant, etc.). Under each question, provide two to four numbered reasons with short, clear paragraphs and embedded short quotes with platform tags. Do not invent percentages or polls; rely only on patterns visible in the comments. If evidence for a reason is weak, say that evidence is limited.

        4) Overall Conclusion  
        After all the question-style opinion blocks, write a short paragraph of two to four sentences. Give a direct conclusion based on the observed opinions. If it is a comparison, state clearly which option the crowd leans toward and why. This section should read like a final recommendation, not a neutral restatement.

        5) Sentiment Snapshot  
        Provide one short paragraph that estimates overall sentiment as Positive, Negative, and Neutral in integer percentages that roughly sum to 100, based only on the given comments. Briefly justify the estimate and mention a couple of representative feelings, with one or two short inline quotes with platform tags.

        6) Comments and Conversation Count  
        Using only the PLATFORM STATS text above, describe in one short paragraph how active the conversation is. Mention posts and comments by platform where possible, total interactions across all platforms, and identify the three busiest platforms by total interactions.

        APPENDIX — Brief Outline  
        At the end, add a short Appendix section that lists three to seven key opinion themes with one sentence each, and then a simple list of the conversation URLs under the heading “Conversation References”.

        CONSTRAINTS  
        Use only the provided data. Avoid speculation. Keep quotes within 30 words and always include platform tags. Keep the whole report compact and decision-oriented, with minimal decoration.
        """.strip()

    completion = client.chat.completions.create(
        model="gpt-5-2025-08-07",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": report_prompt}
        ]
    )
    report_text = completion.choices[0].message.content
    return report_text
 



#******************** Chatot  *************************
def refine_response(user_followup: str, previous_results: str, previous_query: str):
    """
    Generate a concise, refined answer for a user follow-up question
    based on the previous social listening report and context.
    """

    print("\n🔁 Refining answer based on previous context...")

    # System prompt for the follow-up context
    system_prompt = """
                You are a multi-domain expert and advanced prompt engineer providing high-value insights based on the user's context.
                The user previously received a detailed social listening and opinion-mining report. 
                Now, they may ask *any kind of question* — strategic, analytical, advisory, or personal — referencing that context.

                Your goals:
                - Use the previous report as context when relevant.
                - If not relevant, treat the question independently with domain-specific reasoning.
                - Adapt your expertise dynamically (e.g., marketing strategy, crisis management, product roadmap, leadership, or personal guidance).

                Your answer can include:
                1. Interpretation of Intent — clarify what the user seeks or imply it if unstated.
                2. Analytical / Strategic Insight — provide detailed reasoning or evaluation.
                3. Actionable Recommendations — concrete next steps, frameworks, or strategies.
                4. Drawbacks & Risk Factors — highlight trade-offs or limitations.

                Tone & style:
                - Expert, concise, and empathetic.
                - Avoid repeating earlier report sections verbatim.
                - Focus on *clarity, reasoning depth, and applicability*.
                """

    # Construct prompt context for the model
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"Previous user query:\n{previous_query}\n\n"
                f"Previous report summary:\n{previous_results}\n\n"
                f"Follow-up question:\n{user_followup}\n\n"
                "Respond briefly and professionally, focusing only on the follow-up point. "
                "If data doesn't exist in the previous report, state that clearly instead of guessing."
            ),
        },
    ]

    # Generate the refined response
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    refined_text = completion.choices[0].message.content.strip()
    return refined_text
   





