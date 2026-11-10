import streamlit as st
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔬",
    layout="wide",
)

# ── Helper: normalise agent message content ────────────────────────────────────
def extract_text(content) -> str:
    """LangChain message content can be a str or a list of typed blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)


# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🔬 Multi-Agent Research System")
st.caption("Search → Scrape → Write → Critique · Powered by Gemini + LangChain + Tavily")

st.divider()

# ── Input ──────────────────────────────────────────────────────────────────────
topic = st.text_input(
    "Research Topic",
    placeholder="e.g. Impact of war on the stock market",
    label_visibility="visible",
)

run = st.button("▶ Run Research", type="primary", disabled=not topic.strip())

st.divider()

# ── Pipeline ───────────────────────────────────────────────────────────────────
if run and topic.strip():
    state: dict = {}

    with st.status("Running research pipeline …", expanded=True) as pipeline_status:

        # ── Step 1: Search agent ───────────────────────────────────────────────
        st.write("🔍 **Search agent** is gathering information …")
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        state["search_results"] = extract_text(search_result["messages"][-1].content)
        st.write("✅ Search complete.")

        # ── Step 2: Reader agent ───────────────────────────────────────────────
        st.write("📖 **Reader agent** is scraping the most relevant URL …")
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:800]}"
            )]
        })
        state["scraped_content"] = extract_text(reader_result["messages"][-1].content)
        st.write("✅ Scraping complete.")

        # ── Step 3: Writer chain ───────────────────────────────────────────────
        st.write("✍️ **Writer chain** is drafting the report …")
        research_combined = (
            f"Search Results:\n{state['search_results']}\n\n"
            f"Detailed Scraped Content:\n{state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined,
        })
        st.write("✅ Report drafted.")

        # ── Step 4: Critic chain ───────────────────────────────────────────────
        st.write("🧐 **Critic chain** is reviewing the report …")
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        st.write("✅ Review complete.")

        pipeline_status.update(label="Research complete!", state="complete", expanded=False)

    # ── Results ────────────────────────────────────────────────────────────────
    report_tab, critic_tab, raw_tab = st.tabs(["📄 Report", "🧐 Critic Review", "🗂 Raw Data"])

    with report_tab:
        st.markdown(state["report"])

    with critic_tab:
        st.markdown(state["feedback"])

    with raw_tab:
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("🔍 Search Results", expanded=False):
                st.write(state["search_results"])
        with col2:
            with st.expander("📃 Scraped Web Content", expanded=False):
                st.write(state["scraped_content"])
