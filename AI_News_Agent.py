import os
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio

# Ensure there's an active event loop
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Configure the Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    verbose=True,
    temperature=0.5,
    google_api_key=GOOGLE_API_KEY
)

# Initialize the SerperDevTool for internet search capabilities
tool = SerperDevTool(api_key=SERPER_API_KEY)

# Define the Senior Researcher Agent
news_researcher = Agent(
    role="Senior Researcher",
    goal="Uncover groundbreaking technologies in {topic}",
    verbose=True,
    memory=True,
    backstory=(
        "Driven by curiosity, you're at the forefront of innovation, eager to explore and share knowledge that could change the world."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=True
)

# Define the Writer Agent
news_writer = Agent(
    role="Writer",
    goal="Narrate compelling tech stories about {topic}",
    verbose=True,
    memory=True,
    backstory=(
        "With a flair for simplifying complex topics, you craft engaging narratives that captivate and educate, bringing new discoveries to light in an accessible manner."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False
)

# Define the Research Task
research_task = Task(
    description=(
        "Identify the next big trend in {topic}. Focus on identifying pros and cons and the overall narrative. Your final report should clearly articulate the key points, its market opportunities, and potential risks."
    ),
    expected_output="A comprehensive 3-paragraph report on the latest trends in {topic}.",
    tools=[tool],
    agent=news_researcher,
)

# Define the Writing Task
write_task = Task(
    description=(
        "Compose an insightful article on {topic}. Focus on the latest trends and how they're impacting the industry. This article should be easy to understand, engaging, and positive."
    ),
    expected_output="A 4-paragraph article on {topic} advancements formatted as markdown.",
    tools=[tool],
    agent=news_writer,
    async_execution=False,
    output_file='new-blog-post.md'
)

# Assemble the Crew
crew = Crew(
    agents=[news_researcher, news_writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
)

# Streamlit App Configuration
st.set_page_config(page_title="AI-Powered Tech News Generator", page_icon="📰", layout="wide")

# App Title
st.title("📰 Tech News Generator AI Agent")
st.write("Discover and write compelling articles on the latest tech trends with AI assistance.")

# User Input
topic = st.text_input("Enter a technology topic:", "AI in healthcare")

# Button to Start Analysis
start_analysis = st.button("Generate Article")

# Placeholder for Results
result_placeholder = st.empty()

if start_analysis:
    with st.spinner("Analyzing and generating content..."):
        try:
            # Execute the Crew process
            result = crew.kickoff(inputs={'topic': topic})
            # Display the result
            result_placeholder.markdown(result)
        except Exception as e:
            st.error(f"An error occurred: {e}")
