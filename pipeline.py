from agents import build_reader_agent , build_search_agent , writer_chain , critic_chain

def run_research_pipeline(topic : str) -> dict:

    state={}

    # Search agent working
    print("\n\nSearch agent is working ...\n\n")

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user",f"Find recent, reliable and detailed information about: {topic}")]
    })

    state['search_results'] = search_result['messages'][-1].content

    print("\n search result ",state['search_results'])

    # Reader agent working
    print("\n\nReader agent is working ...\n\n")
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
         "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}" #Links will be mostly in the first 800 characters, we can increase if needed.
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nscraped content: \n", state['scraped_content'])

    print("\n\nWriter chain is drafting the report ...\n\n")

    research_combined = (
        f"Search Results:\n{state['search_results']}\n\n"
        f"Detailed Scraped Content:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\n Final Report\n",state['report'])
    
    print("\n\nCritic chain is reviewing the report ...\n\n")

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\n critic report \n", state['feedback'])

    return state

if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)