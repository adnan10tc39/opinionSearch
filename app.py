# app.py
import json
import os
from dotenv import load_dotenv
from typing import Annotated, List, Optional, Dict, Any

# === FastAPI bits (added) ===
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# === Your original imports ===
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from BOL import serp_search
from urls_scrappers import collect_platform_urls

from BOL import ( reddit_comment_retrieval, youtube_post_retrieval, tiktok_post_retrieval,
                  instagram_comments_retrieval, facebook_comments_retrieval,
                  x_comments_retrieval,linkedin_comments_retrieval, results_curation, refine_response)

load_dotenv()

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")

# Initialize State
class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_question: Optional[str]
    max_per_platform: Optional[int]
    google_results: Optional[str]
    bing_results: Optional[str]
    platform_urls: Optional[Dict[str, List[str]]]
    # reddit_comments_data : Optional[List[str]]
    youtube_comments_data : Optional[List[str]]
    tiktok_comments_data : Optional[List[str]]
    instagram_comments_data : Optional[List[str]]
    facebook_comments_data : Optional[List[str]]
    x_comments_data : Optional[List[str]]
    linkedin_comments_data : Optional[List[str]]
    ready :  Optional[bool]
    combined_comments : Optional[dict]
    # comments_metadata : Optional[List[str]]
    final_results : Optional[List[str]]

    
# Google Search
def google_search(state: State):
    print("Getting Google Post")
    user_question = state.get("user_question", "")
    google_results = serp_search(user_question, engine="google")
    return {"google_results": google_results} 

# Bing Search
def bing_search(state: State):
    print("Getting Bing Post")
    user_question = state.get("user_question", "")
    bing_results = serp_search(user_question, engine="bing")
    return {"bing_results": bing_results}

# Social Media URLs
def social_media_urls(state: State):
    user_question = state.get("user_question", "")
    max_per_platform = state.get("max_per_platform", None)
    platform_urls = collect_platform_urls(user_question, max_per_platform)
    return {"platform_urls": platform_urls}

# Reddit comments
# def retrieve_reddit_comments(state: State):
#     selected_urls = state.get("platform_urls", {})
#     reddit_urls = selected_urls.get("Reddit", [])
#     print("Getting Reddit post comments")
#     if not reddit_urls:
#         return {"reddit_comments_data": []}
#     reddit_comments_data = reddit_comment_retrieval(reddit_urls,days_back=10, load_all_replies=False, comment_limit=5)
#     if reddit_comments_data:
#         print(f"Successfully got {len(reddit_comments_data)} Reddit posts")
#     else:
#         print("Failed to get Reddit post data")
#         reddit_comments_data = []
#     return {"reddit_comments_data":reddit_comments_data}

#Youtube Comments
def retrieve_youtube_comments(state: State):
    selected_urls = state.get("platform_urls", {})
    youtube_urls = selected_urls.get("Youtube", [])
    print("Getting youtube post comments")
    if not youtube_urls:
        return {"youtube_comments_data": []}

    youtube_comments_data = youtube_post_retrieval(youtube_urls)

    if youtube_comments_data:
        print(f"Successfully got {len(youtube_comments_data)} Youtube comments")
    else:
        print("Failed to get Youtube comments data")
        youtube_comments_data = []

    return {"youtube_comments_data": youtube_comments_data}

#Tiktok Comments
def retrieve_tiktok_comments(state: State):
    selected_urls = state.get("platform_urls", {})
    tiktok_urls = selected_urls.get("Tiktok", [])
    print("Getting Tiktok post comments")

    if not tiktok_urls:
        return {"tiktok_comments_data": []}
    
    tiktok_urls = tiktok_urls[:1]

    tiktok_comments_data = tiktok_post_retrieval(tiktok_urls)

    if tiktok_comments_data:
        print(f"Successfully got {len(tiktok_comments_data)} Tiktok posts")
    else:
        print("Failed to get Tiktok post data")
        tiktok_comments_data = []

    return {"tiktok_comments_data":tiktok_comments_data}

# Instagram Comments
def retrieve_instagram_comments(state: State):
    selected_urls = state.get("platform_urls", {})
    instagram_urls = selected_urls.get("Instagram", [])
    print("Getting Instagram post comments")

    instagram_comments_data = instagram_comments_retrieval(instagram_urls)

    if instagram_comments_data:
        print(f"Successfully got {len(instagram_comments_data)} Instagram posts")
    else:
        print("Failed to get Instagram post data")
        instagram_comments_data = []

    return {"instagram_comments_data":instagram_comments_data}

# Facebook Comments
def retrieve_facebook_comments(state: State):
    selected_urls = state.get("platform_urls", {})
    facebook_urls = selected_urls.get("Facebook", [])
    print("Getting facebook post comments")

    facebook_comments_data = facebook_comments_retrieval(facebook_urls, get_all_replies=False, limit_records=5, comments_sort="Most relevant")

    if facebook_comments_data:
        print(f"Successfully got {len(facebook_comments_data)} Facebook posts")
    else:
        print("Failed to get Facebook post data")
        facebook_comments_data = []

    return {"facebook_comments_data":facebook_comments_data}

# X Comments
def retrieve_x_comments(state: State):
    selected_urls = state.get("platform_urls", {})
    x_urls = selected_urls.get("X", [])
    print("Getting x post comments")

    x_comments_data = x_comments_retrieval(x_urls)

    if x_comments_data:
        print(f"Successfully got {len(x_comments_data)} X posts")
    else:
        print("Failed to get X post data")
        x_comments_data = []

    return {"x_comments_data":x_comments_data}

# LinkedIn Comments
def retrieve_linkedin_comments(state: State):
    selected_urls = state.get("platform_urls", {})
    linkedin_urls = selected_urls.get("LinkedIn", [])
    print("Getting Linkedin comments")

    linkedin_comments_data = linkedin_comments_retrieval(linkedin_urls)

    if linkedin_comments_data:
        print(f"Successfully got {len(linkedin_comments_data)} LinkedIn posts")
    else:
        print("Failed to get LinkedIn post data")
        linkedin_comments_data = []

    return {"linkedin_comments_data":linkedin_comments_data}

# def social_comments(state: State):
#     # Check if all sources have returned data
#     if all([
#         # state.get("reddit_comments_data"),
#         state.get("youtube_comments_data"),
#         state.get("tiktok_comments_data"),
#         state.get("instagram_comments_data"),
#         state.get("facebook_comments_data"),
#         state.get("x_comments_data"),
#         state.get("linkedin_comments_data")
#     ]):
#         # Proceed to combining comments
#         return {"ready": True}
#     else:
#         # Not all comments arrived yet; wait
#         return {"ready": False}
# def social_comments(state: State):
#     ready = all([
#         state.get("youtube_comments_data"),
#         state.get("tiktok_comments_data"),
#         state.get("instagram_comments_data"),
#         state.get("facebook_comments_data"),
#         state.get("x_comments_data"),
#         state.get("linkedin_comments_data"),
#     ])
#     return {"ready": ready}
def social_comments(state: State):
    keys = [
        "youtube_comments_data",
        "tiktok_comments_data",
        "instagram_comments_data",
        "facebook_comments_data",
        "x_comments_data",
        "linkedin_comments_data",
    ]
    # Ready once every key is set by its fetcher (None -> done), regardless of [] vs list
    ready = all(state.get(k) is not None for k in keys)
    return {"ready": ready}
    
def combine_comments(state: State):
    combined_comments = {
        # "Reddit": state.get("reddit_comments_data", []),
        "Youtube": state.get("youtube_comments_data", []),
        "Tiktok": state.get("tiktok_comments_data", []),
        "Instagram": state.get("instagram_comments_data", []),
        "Facebook": state.get("facebook_comments_data", []),
        "X": state.get("x_comments_data", []),
        "LinkedIn": state.get("linkedin_comments_data", []),
        "Google" : state.get("google_results", []),
        "Bing" : state.get("bing_results", [])
    }
    print("Combined all platform comments.")
    return {"combined_comments": combined_comments}

# def comments_metadata(state: State):
#     selected_urls = state.get("platform_urls", {})
#     return selected_urls

def final_output(state: State):
    selected_urls = state.get("platform_urls", {})
    combined_comments = state.get("combined_comments", {})
    user_question= state.get("user_question",str)
    final_results= results_curation(selected_urls,combined_comments,user_question)
    return {"final_results": final_results}


# def route_if_ready(state: State):
#     return "combine_comments" if state.get("ready") else None 

def route_if_ready(state: State):
    # Only proceed once every retrieval node has *finished* (even if it found nothing)
    if state.get("ready"):
        return ["combine_comments"]   # <- list, not string
    return []

# Initialize graph
graph_builder = StateGraph(State)

graph_builder.add_node("google_search", google_search)
graph_builder.add_node("bing_search", bing_search)
graph_builder.add_node("social_media_urls", social_media_urls)

# graph_builder.add_node("retrieve_reddit_comments", retrieve_reddit_comments)
graph_builder.add_node("retrieve_youtube_comments", retrieve_youtube_comments)
graph_builder.add_node("retrieve_tiktok_comments", retrieve_tiktok_comments)
graph_builder.add_node("retrieve_instagram_comments", retrieve_instagram_comments)
graph_builder.add_node("retrieve_facebook_comments", retrieve_facebook_comments)
graph_builder.add_node("retrieve_x_comments", retrieve_x_comments)
graph_builder.add_node("retrieve_linkedin_comments", retrieve_linkedin_comments)
graph_builder.add_node("social_comments", social_comments)
graph_builder.add_node("combine_comments", combine_comments)
graph_builder.add_node("final_results", final_output)
# graph_builder.add_node("comments_metadata", comments_metadata)

graph_builder.add_edge(START, "google_search")
graph_builder.add_edge(START, "bing_search")
graph_builder.add_edge(START, "social_media_urls")


# graph_builder.add_edge("social_media_urls", "retrieve_reddit_comments")
graph_builder.add_edge("social_media_urls", "retrieve_youtube_comments")
graph_builder.add_edge("social_media_urls", "retrieve_tiktok_comments")
graph_builder.add_edge("social_media_urls", "retrieve_instagram_comments")
graph_builder.add_edge("social_media_urls", "retrieve_facebook_comments")
graph_builder.add_edge("social_media_urls", "retrieve_x_comments")
graph_builder.add_edge("social_media_urls", "retrieve_linkedin_comments")

# graph_builder.add_edge("retrieve_reddit_comments", "social_comments")
graph_builder.add_edge("retrieve_youtube_comments", "social_comments")
graph_builder.add_edge("retrieve_tiktok_comments", "social_comments")
graph_builder.add_edge("retrieve_instagram_comments", "social_comments")
graph_builder.add_edge("retrieve_facebook_comments", "social_comments")
graph_builder.add_edge("retrieve_x_comments", "social_comments")
graph_builder.add_edge("retrieve_linkedin_comments", "social_comments")

graph_builder.add_conditional_edges(
    "social_comments",
    route_if_ready,
    {"combine_comments": "combine_comments"},
)
graph_builder.add_edge("google_search", "combine_comments")
graph_builder.add_edge("bing_search", "combine_comments")
# graph_builder.add_edge("social_comments", "combine_comments")
# graph_builder.add_edge("social_media_urls", "comments_metadata")
graph_builder.add_edge("combine_comments", "final_results")
graph_builder.add_edge("final_results", END)

graph = graph_builder.compile()

# --- Your original CLI helpers (preserved exactly) ---
def perform_research(user_input, conversation_history, no_of_post):
    print("\nStarting parallel research process...")
    print("Launching Google, Bing, Reddit, Facebook, LinkedIn, Instagram, Twitter(X), TikTok, and YouTube searches...\n")

    state = {
        "messages": [{"role": "user", "content": user_input}],
        "user_question": user_input,
        "max_per_platform": no_of_post,
        "google_results": None,
        "bing_results": None,
        "platform_urls": None,
        "youtube_comments_data": None,
        "tiktok_comments_data": None,
        "instagram_comments_data": None,
        "facebook_comments_data": None,
        "x_comments_data": None,
        "linkedin_comments_data": None,
        "ready": None,
        "combined_comments": None,
        "final_results": None,
    }

    final_state = graph.invoke(state)
    final_results = final_state.get("final_results", "No results found.")
    conversation_history.append({"query": user_input, "results": final_results})

    print("\n✅ Final Results:\n")
    print(final_results)
    print("\n" + "-" * 80)
    return final_results


def handle_followups(conversation_history, user_input):
    while True:
        followup = input(
            "\n💬 You can:\n"
            " - Ask a related question\n"
            " - Type 'again' to start a new research\n"
            " - Type 'exit' to quit\n> "
        ).strip().lower()

        if followup == "exit":
            print("👋 Ending chat. Goodbye!")
            return "exit"

        if followup == "again":
            print("\n🔄 Restarting from the beginning...\n")
            return "again"

        if not followup:
            print("⚠️ Please enter a valid follow-up question or type 'exit'/'again'.")
            continue

        all_previous = "\n\n".join(
            [f"Query: {conv['query']}\nResults: {conv['results']}" for conv in conversation_history]
        )

        new_answer = refine_response(followup, all_previous, user_input)
        print("\n" + new_answer)
        print("\n" + "-" * 80)


def run_chatbot():
    conversation_history = []

    while True:
        user_input = input("Ask me anything: ").strip()
        no_of_post = int(input("Enter number of post retreval: "))
        if user_input.lower() == "exit":
            print("Bye")
            break

        perform_research(user_input, conversation_history,no_of_post)

        if handle_followups(conversation_history, user_input) == "exit":
            break


# === FastAPI models & routes (added) ===

class ResearchRequest(BaseModel):
    question: str = Field(..., description="The user question / topic to research.")
    max_per_platform: int = Field(1, ge=1, le=20, description="Max URLs per platform to collect.")
    debug: bool = Field(False, description="If true, include intermediate outputs.")

class ResearchResponse(BaseModel):
    final_results: Any
    debug: Optional[Dict[str, Any]] = None

class RefineRequest(BaseModel):
    followup: str
    conversation_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of dicts like {'query': ..., 'results': ...}"
    )
    original_question: Optional[str] = None

class RefineResponse(BaseModel):
    answer: str

app = FastAPI(title="Multi-Source Research API", version="1.0.0")

# CORS (open by default; tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "has_brightdata_key": bool(BRIGHTDATA_API_KEY),
    }

@app.post("/research", response_model=ResearchResponse)
def research(req: ResearchRequest):
    try:
        state: State = {
            "messages": [{"role": "user", "content": req.question}],
            "user_question": req.question,
            "max_per_platform": req.max_per_platform,
            "google_results": None,
            "bing_results": None,
            "platform_urls": None,
            "youtube_comments_data": None,
            "tiktok_comments_data": None,
            "instagram_comments_data": None,
            "facebook_comments_data": None,
            "x_comments_data": None,
            "linkedin_comments_data": None,
            "ready": None,
            "combined_comments": None,
            "final_results": None,
        }

        final_state = graph.invoke(state)
        final_results = final_state.get("final_results", "No results found.")

        payload: Dict[str, Any] = {"final_results": final_results}
        if req.debug:
            payload["debug"] = {
                "platform_urls": final_state.get("platform_urls"),
                "google_results": final_state.get("google_results"),
                "bing_results": final_state.get("bing_results"),
                "combined_comments": final_state.get("combined_comments"),
            }
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refine", response_model=RefineResponse)
def refine(req: RefineRequest):
    """
    Optional helper to reuse your refine_response in a stateless way.
    Feeds prior conversation results back in to generate a refined answer.
    """
    try:
        all_previous = "\n\n".join(
            [f"Query: {conv.get('query')}\nResults: {conv.get('results')}" for conv in req.conversation_history]
        )
        answer = refine_response(req.followup, all_previous, req.original_question or "")
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Local dev runner: uvicorn app:app --reload
if __name__ == "__main__":
    # Keeping your CLI entrypoint exactly as-is, but not auto-running it here.
    # If you prefer the CLI mode, uncomment the next line.
    # run_chatbot()
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
