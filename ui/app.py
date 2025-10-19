import streamlit as st
import requests
import time

API_URL = "http://localhost:8000"

st.title("DocuMind")

query = st.text_input("Ask a question about your PDFs:")

if 'job_id' not in st.session_state:
    st.session_state['job_id'] = None


# Only show job submission message, not references, on submit
if st.button("Submit") and query:
    response = requests.post(f"{API_URL}/ask", json={"query": query})
    if response.status_code == 200:
        job_id = response.json()["job_id"]
        st.session_state['job_id'] = job_id
        st.success(f"Job submitted! Job ID: {job_id}")
    else:
        st.error("Failed to submit query.")

if st.session_state.get('job_id'):
    st.write(f"Checking status for Job ID: {st.session_state['job_id']}")
    status_url = f"{API_URL}/status/{st.session_state['job_id']}"
    status = None
    status_placeholder = st.empty()
    for _ in range(30):  # Poll for up to 30 seconds
        resp = requests.get(status_url)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "completed":
                status_placeholder.success("Answer ready!")
                st.markdown(f"**🤖 Answer:** {data.get('answer')}")
                refs = data.get("references")
                if refs:
                    st.markdown("**References:**")
                    for ref in refs:
                        page = ref.get('page_number', 'N/A')
                        source = ref.get('source', 'N/A')
                        st.markdown(f"- **Page:** {page} | **Source:** {source}")
                break
            elif data.get("status") == "failed":
                status_placeholder.error(f"Job failed: {data.get('error')}")
                break
            else:
                status_placeholder.info(f"Status: {data.get('status')}. Waiting...")
        else:
            status_placeholder.error("Failed to get job status.")
            break
        time.sleep(1)
    else:
        status_placeholder.warning("Timed out waiting for answer.")
