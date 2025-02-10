import streamlit as st
import pandas as pd
import plotly.express as px
from app.schema import create_connection
from app.view import display_footer
from app.components import main_components
from app.accounts import logout
import time


def is_admin():
    if not st.session_state.get('authenticated'):
        return False
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("""
                SELECT role_id FROM users 
                WHERE email = %s""", (st.session_state.email,))
            result = cursor.fetchone()
            return result and result[0] == 2
    except Exception as e:
        st.error(f"Admin check error: {e}")
        return False
@st.cache_data(ttl=60)  # Refresh data every 60 seconds
def get_resume_data(for_analytics=False):
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            if for_analytics:
                query = """
                    SELECT 
                        ra.uploaded_at AS timestamp,
                        ra.applied_profile AS Applied_for_Profile,
                        ra.professional_experience AS Professional_Experience_in_Years,
                        ra.linkedin,
                        ra.github,
                        MAX(CASE WHEN pn.phone_number IS NOT NULL THEN 1 ELSE 0 END) AS has_phone
                    FROM resume_analysis ra
                    LEFT JOIN phone_numbers pn ON ra.analysis_id = pn.analysis_id
                    GROUP BY ra.analysis_id, ra.uploaded_at, ra.applied_profile, 
                            ra.professional_experience, ra.linkedin, ra.github
                """
            else:
                query = """
                    SELECT 
                        ra.uploaded_at AS timestamp,
                        ra.name AS Name,
                        ra.parsed_email AS Email,
                        GROUP_CONCAT(DISTINCT pn.phone_number) AS Phone_1,
                        GROUP_CONCAT(DISTINCT ad.address) AS Address,
                        ra.highest_education AS Highest_Education,
                        ra.applied_profile AS Applied_for_Profile,
                        ra.professional_experience AS Professional_Experience_in_Years,
                        ra.linkedin AS LinkedIn,
                        ra.github AS GitHub
                    FROM resume_analysis ra
                    LEFT JOIN phone_numbers pn ON ra.analysis_id = pn.analysis_id
                    LEFT JOIN addresses ad ON ra.analysis_id = ad.analysis_id
                    GROUP BY ra.analysis_id, ra.uploaded_at, ra.name, ra.parsed_email, 
                    ra.applied_profile, ra.resume_score, ra.highest_education
                    LIMIT 100
                """

            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)

    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

def run():
    # if not is_admin():
    #     st.error("Unauthorized access. Admins only.")
    #     st.stop()
    main_components()

    col1, col2 = st.columns([13, 1])
    with col1:
        st.markdown(f"""<h3 style="color: #1d3557;">Welcome {st.session_state.username}!</h3>""", unsafe_allow_html=True)
    
    with col2:
        if st.button(" Log Out", key="logout_btn"):
            logout()

    st.markdown("""
        <div style="text-align:center; margin-bottom: -2rem; margin-top: -1.5rem;">
            <h4 style="color: #1d3557; font-weight: bold;">📊 Admin Dashboard</h4>
        </div>
    """, unsafe_allow_html=True)

    # Live search input
    with st.container():
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            search_query = st.text_input(" ", 
                placeholder="Search across all fields 🔍", 
                key="search_input",
                help="Live search across all candidate fields"
            )

    # Get data and apply live filtering
    df = get_resume_data()
    
    if not df.empty:
        df = df.astype(str)
        if search_query:
            search_lower = search_query.lower()
            mask = df.apply(lambda row: row.str.lower().str.contains(search_lower).any(), axis=1)
            df = df[mask]

        column_order = [
            "timestamp",
            "Name", 
            "Email",
            "Phone_1",
            "Address",
            "Highest_Education",
            "Applied_for_Profile",
            "Professional_Experience_in_Years",
            "LinkedIn",
            "GitHub"
        ]
        
        df = df[column_order]
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['LinkedIn'] = df['LinkedIn'].apply(lambda x: x if x.startswith('http') else f'https://{x}')
        df['GitHub'] = df['GitHub'].apply(lambda x: x if x.startswith('http') else f'https://{x}')

        with st.container():
            col1, col2, col3 = st.columns([1, 6, 1])
            with col2:
                st.data_editor(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "LinkedIn": st.column_config.LinkColumn(
                            "LinkedIn",
                            validate=None,
                            max_chars=40
                        ),
                        "GitHub": st.column_config.LinkColumn(
                            "GitHub", 
                            validate=None,
                            max_chars=40
                        ),
                        "timestamp": st.column_config.DatetimeColumn(
                            "Upload Time",
                            format="YYYY-MM-DD HH:mm"
                        ),
                        "Professional_Experience_in_Years": st.column_config.NumberColumn(
                            "Experience (Years)",
                            format="%.1f"
                        )
                    },
                    height=500,
                    key="data_editor"
                )

    else:
        st.info("No resume data found matching your criteria.")

    st.markdown("---")

    st.markdown('''<div style='text-align: center; margin-bottom: -1rem;'><h3 style='color: #1d3557;'> Analytics Overview 📈 </h3></div>''', 
                    unsafe_allow_html=True)
    # Fetch analytics data
    df_analytics = get_resume_data(for_analytics=True)
        

    if not df_analytics.empty:
        # 1. Simplified Pie Chart
        st.markdown('''<div style='text-align: center;margin-left:-2rem; margin-top: 1rem;'><h5 style='color: #1d3557;'> Resume Trends: Popular Job Targets </h5></div>''', 
                    unsafe_allow_html=True)
        profile_counts = df_analytics['Applied_for_Profile'].value_counts().reset_index()
        profile_counts.columns = ['Profile', 'Count']

    # Create the pie chart
    fig = px.pie(
        profile_counts,
        names='Profile',  # Column for pie slice labels
        values='Count',   # Column for pie slice sizes
        hover_data=['Count'],  # Additional data to show on hover
        
    )

    # Customize hover template and layout
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Applications: %{value}<br>",
        textinfo='percent+label',  # Display percentage and label
        )

    # Adjust layout
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0.5)",
        plot_bgcolor='white',
        showlegend=True,  # Hide legend
        height=500,  # Set chart height
        width=1900,   # Set chart width for 4:6 aspect ratio
        margin=dict(t=5, b=15, l=80, r=0)  # Reduce margins
    )
    
    col1, col2, col3 = st.columns([2, 4, 2])  # Adjust the middle column width for centering
    with col2:
        st.plotly_chart(fig, use_container_width=False)

    with st.container():
    # Get analytics data
        df_analytics = get_resume_data(for_analytics=True)
    st.markdown("---")
    col1, col2, col3 = st.columns([3, 4,3])
    with col2:

        st.markdown('''<div style='text-align: center; margin-bottom: -1rem;'><h4 style='color: #1d3557;'> Presence on Essential Platforms </h4></div>''', 
                    unsafe_allow_html=True)


        if not df_analytics.empty:
            # Calculate metrics
            total_users = len(df_analytics)
            linkedin_users = df_analytics['linkedin'].apply(lambda x: x not in ['', 'N/A', 'nan']).sum()
            github_users = df_analytics['github'].apply(lambda x: x not in ['', 'N/A', 'nan']).sum()
            
            # Create comparison data
            comparison_data = pd.DataFrame({
                'Category': ['LinkedIn', 'GitHub'],
                'Total Users': [total_users, total_users],
                'Platform Users': [linkedin_users, github_users]
            })

            # Create melted dataframe for plotting
            plot_data = comparison_data.melt(
                id_vars='Category', 
                value_vars=['Total Users', 'Platform Users'],
                var_name='Metric',
                value_name='Count'
            )

            # Create grouped bar chart
            fig = px.bar(
                plot_data,
                x='Category',
                y='Count',
                color='Metric',
                barmode='group',
                color_discrete_map={
                    'Total Users': '#1f77b4',  # Navy blue
                    'Platform Users': '#2ca02c'  # Green
                },
                text_auto=True,
                template='plotly_white'
            )

            # Add styling
            fig.update_layout(
                xaxis_title="Platform",
                yaxis_title="User Count",
                showlegend=True,
                height=500,
                margin=dict(t=30, b=10),
                paper_bgcolor="rgba(255,255,255,0.6)",
                plot_bgcolor='white',
                xaxis={'categoryorder':'array', 'categoryarray':['LinkedIn', 'GitHub']}
            )

            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        # Clean the experience data
        df_analytics['Professional_Experience_in_Years'] = pd.to_numeric(
            df_analytics['Professional_Experience_in_Years'], 
            errors='coerce'
        ).fillna(0)

        # Prepare experience data
        exp_data = df_analytics['Professional_Experience_in_Years'].value_counts().sort_index().reset_index()
        exp_data.columns = ['Years', 'Count']
        
        # Create Plotly line chart
        fig = px.line(
            exp_data,  # Your cleaned DataFrame
            x='Years',  # X-axis column
            y='Count',  # Y-axis column
            title='Professional Experience Distribution',
            markers=True  # Show markers on the line
        )
        
        # Add average experience line
        avg_exp = df_analytics['Professional_Experience_in_Years'].mean()
        fig.add_shape(
            type="line",
            x0=avg_exp, y0=0,
            x1=avg_exp, y1=max(exp_data['Count']),
            line=dict(color="Red", width=2, dash="dash")
        )
        fig.add_annotation(
            x=avg_exp, y=max(exp_data['Count']),
            text=f'Average: {avg_exp:.1f} years',
            showarrow=True,
            arrowhead=1
        )
        
        st.plotly_chart(fig, use_container_width=True)
    display_footer()