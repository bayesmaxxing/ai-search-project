import streamlit as st
import asyncio
import pandas as pd
import os
import plotly.graph_objects as go
from dotenv import load_dotenv
load_dotenv() 
from demo_runner import run_all, add_sentiment_analysis, run_analysis

st.set_page_config(
    page_title="AI Search Analytics",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        background-color: white;
        color: #1f2937;  /* Dark gray text for main content */
    }
    
    /* Set background color for the entire app */
    .stApp {
        background-color: white;
    }
    
    /* Ensure all text is visible */
    .stMarkdown, .stText, .stDataFrame, .stSelectbox, .stTextInput, .stTextArea, .stNumberInput {
        color: #1f2937 !important;  /* Dark gray text */
    }

    /* Ensure table text is visible */
    .stDataFrame td, .stDataFrame th {
        color: #1f2937 !important;
    }

    /* Ensure selectbox text is visible */
    .stSelectbox > div > div > div {
        color: #1f2937 !important;
    }

    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        color: #1f2937 !important;
        background-color: #f8fafc !important;  /* Light gray background */
        border: 1px solid #e2e8f0 !important;
        caret-color: #1f2937 !important;  /* Make cursor black */
    }

    /* Make text input labels darker */
    .stTextInput label,
    .stTextArea label,
    .stNumberInput label,
    .stSelectbox label {
        color: #1f2937 !important;  /* Dark gray text */
        font-weight: 500 !important;
    }

    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: #f8fafc !important;  /* Light gray background */
        border: 1px solid #e2e8f0 !important;
    }

    /* Dataframe styling */
    .stDataFrame {
        background-color: #f8fafc !important;  /* Light gray background */
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem 0;
        margin: -2rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        text-align: center;
        color: #1f2937;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e1e8ed;
    }
    
    .app-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: #1f2937;
    }
    
    .app-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        color: #4b5563;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border: 1px solid #e1e8ed;
        margin: 1rem 0;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8fafc;
        padding: 0.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        border: none;
        transition: all 0.2s ease;
        color: #4b5563;  /* Adding text color for unselected tabs */
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        color: #3b82f6;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Input styling */
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Chart styling */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e1e8ed;
        color: #1f2937 !important;
        font-weight: 500 !important;
    }
    
    /* Make expander content text darker */
    .streamlit-expanderContent {
        color: #1f2937 !important;
    }

    /* Make info messages darker */
    .stInfo p {
        color: #1f2937 !important;
        font-weight: 500 !important;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #3b82f6;
    }
    
    /* Make spinner text darker */
    .stSpinner p {
        color: #1f2937 !important;
        font-weight: 500 !important;
    }
    
    /* Section headers */
    .section-header {
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e1e8ed;
    }
    
    /* Success/info messages */
    .stSuccess, .stInfo {
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }

    /* Make success and info message text darker */
    .stSuccess p, .stInfo p {
        color: #1f2937 !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("""
<div class="app-header">
    <h1>🔍 AI Search Analytics</h1>
    <p>Measure and optimize your brand's presence in AI-powered search results</p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Input", 
    "Brand Analysis", 
    "Sentiment", 
    "URL Analysis", 
    "Strategy (LLM analysis)", 
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
    st.markdown('<div class="section-header">Configure Your Analysis</div>', unsafe_allow_html=True)
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Brand Configuration**")
        brand = st.text_input("Target Brand", value="Avanza", help="The brand you want to analyze")
        competitor = st.text_input("Main Competitor", value="Nordnet", help="Primary competitor to compare against")
        
        st.markdown("**Search Queries**")
        queries_raw = st.text_area(
            "Queries (one per line)",
            "What to use for investing in stocks in Sweden?\n"
            "How can I trade stocks in Sweden?\n"
            "What's the most user-friendly stock trading platform in Sweden?",
            height=120,
            help="Enter the search queries you want to test, one per line"
        )
        
    with col2:
        st.markdown("**Analysis Settings**")
        repeat_count = st.number_input(
            "🔁 Repeat Count", 
            value=1, 
            min_value=1, 
            max_value=10, 
            step=1,
            help="Number of times to repeat each query for more reliable results"
        )
        
        # Add some information cards
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">4</div>
            <div class="metric-label">AI Search Providers</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Center the run button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Run Analysis", use_container_width=True):
            queries = [q.strip() for q in queries_raw.splitlines() if q.strip()]
            if not queries:
                st.error("Please enter at least one query.")
                st.stop()

            with st.spinner("🔄 Analyzing across AI search providers... This may take ~60 seconds"):
                results = asyncio.run(run_all(brand, competitor, queries, repeat_count))
                results = add_sentiment_analysis(results)
                st.session_state.results = results
                st.session_state.show_results = True
                st.success("✅ Analysis completed! Check the results in the tabs above.")

# Only show other tabs if we have results
if st.session_state.show_results and st.session_state.results is not None:
    df = pd.DataFrame(st.session_state.results)
    
    # Tab 2: Brand & Competitor Analysis
    with tab2:
        st.markdown('<div class="section-header">Brand Performance Overview</div>', unsafe_allow_html=True)
        
        # Calculate overall metrics
        total_queries = len(df)
        brand_mentions = df['brand_mention'].sum()
        competitor_mentions = df['competitor_mention'].sum()
        brand_rate = (brand_mentions / total_queries * 100)
        competitor_rate = (competitor_mentions / total_queries * 100)
        
        # Top level metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{brand_rate:.1f}%</div>
                <div class="metric-label">Brand Mention Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{competitor_rate:.1f}%</div>
                <div class="metric-label">Competitor Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_queries}</div>
                <div class="metric-label">Total Queries</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            advantage = brand_rate - competitor_rate
            color = "#10b981" if advantage > 0 else "#ef4444"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {color};">{advantage:+.1f}%</div>
                <div class="metric-label">Brand Advantage</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### Provider Breakdown")
        
        # Provider analysis
        summary_df = df.groupby('provider_name').agg({
            'brand_mention': ['count', 'sum'],
            'competitor_mention': ['sum']
        }).reset_index()
        summary_df.columns = ['Provider', 'Total Queries', 'Brand Mentions', 'Competitor Mentions']
        summary_df['Brand Mention Rate'] = (summary_df['Brand Mentions'] / summary_df['Total Queries'] * 100).round(1)
        summary_df['Competitor Mention Rate'] = (summary_df['Competitor Mentions'] / summary_df['Total Queries'] * 100).round(1)
        
        # Enhanced chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name=brand,
            x=summary_df['Provider'],
            y=summary_df['Brand Mention Rate'],
            marker_color='#3b82f6',
            text=summary_df['Brand Mention Rate'].apply(lambda x: f'{x}%'),
            textposition='auto'
        ))
        fig.add_trace(go.Bar(
            name=competitor,
            x=summary_df['Provider'],
            y=summary_df['Competitor Mention Rate'],
            marker_color='#ec4899',
            text=summary_df['Competitor Mention Rate'].apply(lambda x: f'{x}%'),
            textposition='auto'
        ))
        fig.update_layout(
            title={
                'text': 'Brand vs Competitor Mention Rates by AI Search Provider',
                'x': 0.5,
                'font': {'size': 18, 'color': '#1f2937'}
            },
            xaxis_title='AI Search Provider',
            yaxis_title='Mention Rate (%)',
            barmode='group',
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': '#1f2937'},
            legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1}
        )
        fig.update_xaxes(showgrid=False, tickfont={'color': '#1f2937'})
        fig.update_yaxes(showgrid=True, gridcolor='#e1e8ed', tickfont={'color': '#1f2937'})
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table with better formatting
        st.markdown("### Detailed Results")
        st.dataframe(
            summary_df.style.format({
                'Brand Mention Rate': '{:.1f}%',
                'Competitor Mention Rate': '{:.1f}%'
            }),
            use_container_width=True
        )

    # Tab 3: Sentiment Analysis
    with tab3:
        st.markdown('<div class="section-header">Brand Sentiment Analysis</div>', unsafe_allow_html=True)
        
        if 'sentiment' in df.columns:
            sentiment_counts = df['sentiment'].value_counts().reindex([
                'Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive'
            ], fill_value=0)
            
            # Calculate sentiment metrics
            total_sentiments = sentiment_counts.sum()
            positive_sentiments = sentiment_counts.get('Positive', 0) + sentiment_counts.get('Very Positive', 0)
            negative_sentiments = sentiment_counts.get('Negative', 0) + sentiment_counts.get('Very Negative', 0)
            neutral_sentiments = sentiment_counts.get('Neutral', 0)
            
            # Top level sentiment metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                positive_rate = (positive_sentiments / total_sentiments * 100) if total_sentiments > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #10b981;">{positive_rate:.1f}%</div>
                    <div class="metric-label">Positive Sentiment</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                negative_rate = (negative_sentiments / total_sentiments * 100) if total_sentiments > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #ef4444;">{negative_rate:.1f}%</div>
                    <div class="metric-label">Negative Sentiment</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                neutral_rate = (neutral_sentiments / total_sentiments * 100) if total_sentiments > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #6b7280;">{neutral_rate:.1f}%</div>
                    <div class="metric-label">Neutral Sentiment</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                sentiment_score = positive_rate - negative_rate
                score_color = "#10b981" if sentiment_score > 0 else "#ef4444" if sentiment_score < 0 else "#6b7280"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {score_color};">{sentiment_score:+.1f}</div>
                    <div class="metric-label">Net Sentiment Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Enhanced sentiment chart
            colors = {
                'Very Negative': '#dc2626',
                'Negative': '#f87171', 
                'Neutral': '#9ca3af',
                'Positive': '#34d399',
                'Very Positive': '#10b981'
            }
            
            fig = go.Figure(data=[
                go.Bar(
                    x=sentiment_counts.index,
                    y=sentiment_counts.values,
                    marker_color=[colors[sentiment] for sentiment in sentiment_counts.index],
                    text=sentiment_counts.values,
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title={
                    'text': f'Sentiment Distribution for {brand} Mentions',
                    'x': 0.5,
                    'font': {'size': 18, 'color': '#1f2937'}
                },
                xaxis_title='Sentiment Category',
                yaxis_title='Number of Mentions',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#1f2937'},
                showlegend=False
            )
            fig.update_xaxes(showgrid=False, tickfont={'color': '#1f2937'})
            fig.update_yaxes(showgrid=True, gridcolor='#e1e8ed', tickfont={'color': '#1f2937'})
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Sentiment breakdown table
            col1, col2 = st.columns([2, 1])
            with col2:
                st.markdown("### Summary")
                sentiment_df = sentiment_counts.reset_index()
                sentiment_df.columns = ['Sentiment', 'Count']
                sentiment_df['Percentage'] = (sentiment_df['Count'] / total_sentiments * 100).round(1)
                st.dataframe(
                    sentiment_df.style.format({'Percentage': '{:.1f}%'}),
                    hide_index=True,
                    use_container_width=True
                )
        else:
            st.info("💡 Sentiment analysis will be available after running the analysis with brand mentions.")

    # Tab 4: URL Domain Analysis
    with tab4:
        st.markdown('<div class="section-header">URL Domain Analysis</div>', unsafe_allow_html=True)
        
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
        
        # Calculate totals for metrics
        total_brand_domains = url_domain_df['Brand Domain Mentions'].sum()
        total_competitor_domains = url_domain_df['Competitor Domain Mentions'].sum()
        total_domains = total_brand_domains + total_competitor_domains
        
        # Top level URL metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_brand_domains}</div>
                <div class="metric-label">Brand URL Citations</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_competitor_domains}</div>
                <div class="metric-label">Competitor URL Citations</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            brand_url_share = (total_brand_domains / total_domains * 100) if total_domains > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{brand_url_share:.1f}%</div>
                <div class="metric-label">Brand URL Share</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            domain_advantage = total_brand_domains - total_competitor_domains
            color = "#10b981" if domain_advantage > 0 else "#ef4444"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {color};">{domain_advantage:+d}</div>
                <div class="metric-label">Citation Advantage</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### Domain Citations by Provider")
        
        # Enhanced chart for domain mentions
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name=brand,
            x=url_domain_df['Provider'],
            y=url_domain_df['Brand Domain Mentions'],
            marker_color='#3b82f6',
            text=url_domain_df['Brand Domain Mentions'],
            textposition='auto'
        ))
        fig2.add_trace(go.Bar(
            name=competitor,
            x=url_domain_df['Provider'],
            y=url_domain_df['Competitor Domain Mentions'],
            marker_color='#ec4899',
            text=url_domain_df['Competitor Domain Mentions'],
            textposition='auto'
        ))
        fig2.update_layout(
            title={
                'text': 'Domain Citations in AI Search Results',
                'x': 0.5,
                'font': {'size': 18, 'color': '#1f2937'}
            },
            xaxis_title='AI Search Provider',
            yaxis_title='Number of URL Citations',
            barmode='group',
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': '#1f2937'},
            legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1}
        )
        fig2.update_xaxes(showgrid=False, tickfont={'color': '#1f2937'})
        fig2.update_yaxes(showgrid=True, gridcolor='#e1e8ed', tickfont={'color': '#1f2937'})
        
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("### Detailed Breakdown")
        st.dataframe(url_domain_df, use_container_width=True)
        
        st.info("💡 URL citations indicate how often each brand's domain appears in the source links provided by AI search engines.")

    # Tab 5: Strategic Analysis
    with tab5:
        st.markdown('<div class="section-header">AI-Powered Strategic Recommendations</div>', unsafe_allow_html=True)
        
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
        with st.expander("🔧 Customize Analysis Prompt", expanded=False):
            edited_prompt = st.text_area(
                "Edit the analysis prompt if desired:",
                value=st.session_state.analysis_prompt,
                height=300,
                help="Customize the prompt to focus on specific aspects of your brand strategy"
            )
            if edited_prompt != st.session_state.analysis_prompt:
                st.session_state.analysis_prompt = edited_prompt
                st.info("✅ Analysis prompt has been updated. Click 'Generate Strategic Analysis' to use the new prompt.")
        
        # Center the analysis button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Generate Strategic Analysis", use_container_width=True):
                with st.spinner("🤖 AI is analyzing your data and generating strategic recommendations..."):
                    analysis_result = asyncio.run(run_analysis(st.session_state.analysis_prompt))
                    st.session_state.analysis_result = analysis_result
                    st.success("✅ Strategic analysis completed!")
                    st.rerun()

        # Display analysis result if it exists
        if st.session_state.analysis_result:
            st.markdown("### Strategic Recommendations")
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
                           padding: 2rem; border-radius: 12px; border-left: 4px solid #3b82f6; 
                           margin: 1rem 0; color: #1f2937; border: 1px solid #e1e8ed;">
                    {st.session_state.analysis_result}
                </div>
                """, 
                unsafe_allow_html=True
            )
        

    # Tab 6: Raw Results
    with tab6:
        st.markdown('<div class="section-header">Detailed Query Results</div>', unsafe_allow_html=True)
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        with col1:
            provider_filter = st.selectbox(
                "Filter by Provider",
                ["All"] + list(df['provider_name'].unique()),
                key="provider_filter"
            )
        with col2:
            brand_filter = st.selectbox(
                "Brand Mentions",
                ["All", "With Brand Mention", "Without Brand Mention"],
                key="brand_filter"
            )
        with col3:
            if 'sentiment' in df.columns:
                sentiment_filter = st.selectbox(
                    "Filter by Sentiment",
                    ["All"] + list(df['sentiment'].dropna().unique()),
                    key="sentiment_filter"
                )
        
        # Apply filters
        filtered_df = df.copy()
        if provider_filter != "All":
            filtered_df = filtered_df[filtered_df['provider_name'] == provider_filter]
        if brand_filter == "With Brand Mention":
            filtered_df = filtered_df[filtered_df['brand_mention'] == 1]
        elif brand_filter == "Without Brand Mention":
            filtered_df = filtered_df[filtered_df['brand_mention'] == 0]
        if 'sentiment' in df.columns and 'sentiment_filter' in locals() and sentiment_filter != "All":
            filtered_df = filtered_df[filtered_df['sentiment'] == sentiment_filter]
        
        st.markdown(f"**Showing {len(filtered_df)} of {len(df)} results**")
        
        # Summary table
        columns_to_show = ["provider_name", "query_text", "brand_mention", "competitor_mention"]
        if 'sentiment' in filtered_df.columns:
            columns_to_show.append("sentiment")
        columns_to_show.append("response_text")
        
        st.dataframe(
            filtered_df[columns_to_show],
            use_container_width=True,
            column_config={
                "provider_name": "Provider",
                "query_text": "Query",
                "brand_mention": st.column_config.CheckboxColumn("Brand Mentioned"),
                "competitor_mention": st.column_config.CheckboxColumn("Competitor Mentioned"),
                "sentiment": "Sentiment",
                "response_text": st.column_config.TextColumn("Response", width="large")
            }
        )
        
        st.markdown("### Detailed Responses")
        
        # Expanders for details with better formatting
        for idx, row in filtered_df.iterrows():
            # Create a more descriptive title
            brand_status = "✅ Brand" if row['brand_mention'] else "❌ No Brand"
            competitor_status = "✅ Competitor" if row['competitor_mention'] else "❌ No Competitor"
            sentiment_status = f"😊 {row.get('sentiment', 'N/A')}" if 'sentiment' in row else ""
            
            title = f"{row['provider_name']} | {brand_status} | {competitor_status} | {sentiment_status} | {row['query_text'][:50]}..."
            
            with st.expander(title):
                # Create columns for better layout
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown("**Analysis Results:**")
                    st.markdown(f"🎯 **Brand Mentioned:** {'Yes' if row['brand_mention'] else 'No'}")
                    st.markdown(f"🏢 **Competitor Mentioned:** {'Yes' if row['competitor_mention'] else 'No'}")
                    
                    if row.get("brand_mention_context"):
                        st.markdown("**Brand Context:**")
                        st.info(row['brand_mention_context'])
                        
                    if 'sentiment' in row and row['sentiment']:
                        st.markdown(f"**Sentiment:** {row['sentiment']}")
                
                with col2:
                    st.markdown("**Full AI Response:**")
                    st.markdown(
                        f"""
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; 
                                   border-left: 3px solid #3b82f6; font-size: 0.9rem; color: #1f2937;">
                            {row['response_text']}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    
                    if row.get("search_urls"):
                        st.markdown("**Source URLs:**")
                        for i, url in enumerate(row["search_urls"], 1):
                            if isinstance(url, tuple):
                                st.markdown(f"{i}. [{url[0]}]({url[1]})")
                            else:
                                st.markdown(f"{i}. {url}")
