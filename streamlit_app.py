import streamlit as st
import asyncio
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv() 
from demo_runner import run_all, add_sentiment_analysis

st.set_page_config(page_title="AI Search-Metrics Demo", layout="wide")
st.title("💡 AI-powered Brand Monitoring (demo)")

with st.form(key="input_form"):
    brand       = st.text_input("Target brand",  value="Avanza")
    competitor  = st.text_input("Competitor",    value="Nordnet")
    queries_raw = st.text_area(
        "Queries (one per line)",
        "What to use for investing in stocks in Sweden?\n"
        "How can I trade stocks in Sweden?\n"
        "What's the most user-friendly stock trading platform in Sweden?"
    )
    submitted = st.form_submit_button("Run demo")

if submitted:
    queries = [q.strip() for q in queries_raw.splitlines() if q.strip()]
    if not queries:
        st.error("Please enter at least one query.")
        st.stop()

    with st.spinner("Calling LLMs… this may take ~60 s"):
        results = asyncio.run(run_all(brand, competitor, queries))
        # Add sentiment analysis after getting results
        
        results = add_sentiment_analysis(results)

    # Turn list-of-dicts into a DataFrame for pretty display
    df = pd.DataFrame(results)
    # Show only the interesting columns in the main table
    # Add summary statistics
    st.subheader("📈 Brand & Competitor Mention Summary")
    summary_df = df.groupby('provider_name').agg({
        'brand_mention': ['count', 'sum'],
        'competitor_mention': ['sum']
    }).reset_index()
    summary_df.columns = ['Provider', 'Total Queries', 'Brand Mentions', 'Competitor Mentions']
    summary_df['Brand Mention Rate'] = (summary_df['Brand Mentions'] / summary_df['Total Queries'] * 100).round(1)
    summary_df['Competitor Mention Rate'] = (summary_df['Competitor Mentions'] / summary_df['Total Queries'] * 100).round(1)
    st.dataframe(
        summary_df,
        use_container_width=True
    )

    # Add bar chart
    st.bar_chart(
        summary_df.set_index('Provider')[['Brand Mention Rate', 'Competitor Mention Rate']],
        color=['#FF4B4B', '#00BFFF']
    )
    st.caption("Brand and competitor mention rates by provider (%)")

    # Add sentiment distribution chart
    if 'sentiment' in df.columns:
        st.subheader("😊 Sentiment Distribution")
        sentiment_counts = df['sentiment'].value_counts().reindex([
            'Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive'
        ], fill_value=0)
        
        # Create two columns for the chart and the data
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.bar_chart(sentiment_counts, color='#4CAF50')
            st.caption("Distribution of sentiment across all brand mentions")
        
        with col2:
            st.dataframe(
                sentiment_counts.reset_index().rename(columns={'index': 'Sentiment', 'sentiment': 'Count'}),
                hide_index=True
            )
    
    st.subheader("📊 Results")
    st.dataframe(
        df[["provider_name", "query_text", "brand_mention", "competitor_mention", "sentiment", "response_text"]],
        use_container_width=True
    )

    # Expanders for details
    for _, row in df.iterrows():
        with st.expander(f'{row["provider_name"]} – {row["query_text"][:40]}…'):
            st.markdown(f"**Brand mention?** {row['brand_mention']}")
            st.markdown(f"**Competitor mention?** {row['competitor_mention']}")
            if row["brand_mention_context"]:
                st.markdown(f"**Brand Context:**\n> {row['brand_mention_context']}")
                if "sentiment" in row:
                    st.markdown(f"**Sentiment:** {row['sentiment']}")                
            st.markdown("---")
            st.markdown("**Full response:**")
            st.write(row["response_text"])
            st.markdown("**Search URLs:**")
            for url in row["search_urls"]:
                st.write(f"- {url}")
