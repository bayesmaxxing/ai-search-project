import streamlit as st
import asyncio
import pandas as pd
import os
import plotly.graph_objects as go
from dotenv import load_dotenv
load_dotenv() 
from demo_runner import run_all, add_sentiment_analysis, run_analysis

st.set_page_config(page_title="AI Search-Metrics Demo", layout="wide")
st.title("💡 AI-Search Optimizer")

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Input", 
    "📈 Brand Analysis", 
    "😊 Sentiment", 
    "🔗 URL Analysis", 
    "🎯 Strategy (LLM analysis)", 
    "Raw Results"
])

# Initialize session state variables if they don't exist
if 'results' not in st.session_state:
    st.session_state.results = None
if 'analysis_prompt' not in st.session_state:
    st.session_state.analysis_prompt = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Tab 1: Input Parameters
with tab1:
    st.subheader("Input Parameters")
    brand = st.text_input("Target brand", value="Avanza")
    competitor = st.text_input("Competitor", value="Nordnet")
    queries_raw = st.text_area(
        "Queries (one per line)",
        "What to use for investing in stocks in Sweden?\n"
        "How can I trade stocks in Sweden?\n"
        "What's the most user-friendly stock trading platform in Sweden?"
    )
    repeat_count = st.number_input("Repeat count", value=1, min_value=1, max_value=10, step=1)
    
    if st.button("Run Demo"):
        queries = [q.strip() for q in queries_raw.splitlines() if q.strip()]
        if not queries:
            st.error("Please enter at least one query.")
            st.stop()

        with st.spinner("Calling LLMs… this may take ~60 s"):
            results = asyncio.run(run_all(brand, competitor, queries, repeat_count))
            results = add_sentiment_analysis(results)
            st.session_state.results = results
            st.session_state.show_results = True

# Only show other tabs if we have results
if st.session_state.show_results and st.session_state.results is not None:
    df = pd.DataFrame(st.session_state.results)
    
    # Tab 2: Brand & Competitor Analysis
    with tab2:
        st.subheader("Brand & Competitor Mention Summary")
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

        # Add bar chart for mention rates
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Brand',
            x=summary_df['Provider'],
            y=summary_df['Brand Mention Rate'],
            marker_color='#FF4B4B'
        ))
        fig.add_trace(go.Bar(
            name='Competitor',
            x=summary_df['Provider'],
            y=summary_df['Competitor Mention Rate'],
            marker_color='#00BFFF'
        ))
        fig.update_layout(
            title='Brand and Competitor Mention Rates by Provider',
            xaxis_title='Provider',
            yaxis_title='Mention Rate (%)',
            barmode='group',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Brand and competitor mention rates by provider (%)")

    # Tab 3: Sentiment Analysis
    with tab3:
        st.subheader("Sentiment Distribution")
        if 'sentiment' in df.columns:
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

    # Tab 4: URL Domain Analysis
    with tab4:
        st.subheader("Search URL Domain Analysis")
        
        # Count domain mentions in URLs
        brand_domain = brand.lower()
        competitor_domain = competitor.lower()
        
        url_domain_counts = {
            'Provider': [],
            'Brand Domain Mentions': [],
            'Competitor Domain Mentions': []
        }
        
        for provider in df['provider_name'].unique():
            provider_urls = df[df['provider_name'] == provider]['search_urls'].explode()
            brand_count = sum(1 for url in provider_urls if (
                (isinstance(url, tuple) and brand_domain in url[1].lower()) or
                (isinstance(url, str) and brand_domain in url.lower())
            ))
            competitor_count = sum(1 for url in provider_urls if (
                (isinstance(url, tuple) and competitor_domain in url[1].lower()) or
                (isinstance(url, str) and competitor_domain in url.lower())
            ))
        
            url_domain_counts['Provider'].append(provider)
            url_domain_counts['Brand Domain Mentions'].append(brand_count)
            url_domain_counts['Competitor Domain Mentions'].append(competitor_count)
        
        url_domain_df = pd.DataFrame(url_domain_counts)
        st.dataframe(url_domain_df, use_container_width=True)
        
        # Add bar chart for domain mentions
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name='Brand',
            x=url_domain_df['Provider'],
            y=url_domain_df['Brand Domain Mentions'],
            marker_color='#FF4B4B'
        ))
        fig2.add_trace(go.Bar(
            name='Competitor',
            x=url_domain_df['Provider'],
            y=url_domain_df['Competitor Domain Mentions'],
            marker_color='#00BFFF'
        ))
        fig2.update_layout(
            title='Brand and Competitor Domain Mentions by Provider',
            xaxis_title='Provider',
            yaxis_title='Number of Mentions',
            barmode='group',
            showlegend=True
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Number of times each brand's domain appears in search URLs")

    # Tab 5: Strategic Analysis
    with tab5:
        st.subheader("Strategic Analysis")
        
        # Calculate key metrics for the prompt
        total_queries = len(df)
        brand_mention_rate = (df['brand_mention'].sum() / total_queries * 100).round(1)
        competitor_mention_rate = (df['competitor_mention'].sum() / total_queries * 100).round(1)
        
        # Calculate total domain mentions
        total_brand_domains = url_domain_df['Brand Domain Mentions'].sum()
        total_competitor_domains = url_domain_df['Competitor Domain Mentions'].sum()
        
        # Calculate sentiment distribution
        sentiment_distribution = df['sentiment'].value_counts().to_dict()
        
        # Create the analysis prompt
        analysis_prompt = f"""You are a highly specialized marketing expert with a deep understanding of **large language model (LLM)-powered search and generative AI in search results**. You are renowned for your ability to analyze search data and provide highly specific and actionable recommendations that leverage the unique characteristics of AI search.

Your recommendations must be specific, actionable, and include a clear explanation of **why** the recommendation is beneficial in the context of how LLMs process information and generate search results. Focus on strategies that can be implemented within the next 3-6 months.

Based on the following search analysis data for {brand}:

**1. Brand Performance in LLM-Powered Search:**
   - Brand mention rate in generative AI answers: {brand_mention_rate}%
   - Total brand domain mentions in URLs within AI-generated content: {total_brand_domains}
   - Sentiment distribution of brand mentions in AI search: {sentiment_distribution} (e.g., Positive: X%, Negative: Y%, Neutral: Z%)

**2. Overall Search Context:**
   - Total queries analyzed: {total_queries}
   - Search providers (specify if any are known to heavily utilize LLMs): {', '.join(df['provider_name'].unique())}

Please provide specific, actionable recommendations for how {brand} could improve their marketing strategy to:

1. **Increase their mention rate in LLM-powered search results (both generative answers and AI-powered snippets/summaries).** Explain how the recommendation leverages LLM information processing.
2. **Improve their domain visibility in the URLs cited within AI-generated content.** Explain how this aligns with LLM sourcing and credibility assessment.
3. **Enhance positive sentiment and mitigate negative sentiment in brand mentions within AI search.** Explain how this relates to LLM understanding and presentation of sentiment.

For each recommendation, provide:
* **Specific Action:** A concrete step to take.
* **Reasoning (linked to AI search):** Why this action is likely to be effective in the context of LLM-powered search.
* **Key Metrics for Tracking Success:** How you would measure the impact of this action."""

        # Store the prompt in session state
        st.session_state.analysis_prompt = analysis_prompt

        # Display the prompt in an expander
        with st.expander("View and Edit Analysis Prompt"):
            edited_prompt = st.text_area(
                "Edit the analysis prompt if desired:",
                value=st.session_state.analysis_prompt,
                height=300
            )
            if edited_prompt != st.session_state.analysis_prompt:
                st.session_state.analysis_prompt = edited_prompt
                st.info("Analysis prompt has been updated. Click 'Run Analysis' to use the new prompt.")
        
        # Add a button to run the analysis
        if st.button("Run Analysis"):
            with st.spinner("Generating analysis..."):
                analysis_result = asyncio.run(run_analysis(st.session_state.analysis_prompt))
                st.session_state.analysis_result = analysis_result
                st.rerun()

        # Display analysis result if it exists
        if st.session_state.analysis_result:
            st.subheader("🤖 AI Analysis")
            st.markdown(st.session_state.analysis_result)
        

    # Tab 6: Raw Results
    with tab6:
        st.subheader("Raw Results")
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
