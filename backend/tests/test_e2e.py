import pytest
from playwright.sync_api import Page, expect

# NOTE: For these tests to pass, the Frontend (5173) and Backend (8000) must be running locally.

def test_dashboard_load(page: Page):
    """Verify the dashboard loads with the correct branding."""
    page.goto("http://localhost:5173")
    
    # Check for title
    expect(page.get_by_text("HireIQ SWARM")).to_be_visible()
    
    # Check for search input
    expect(page.get_by_placeholder("Ask about roles, skills, or salary trends in India...")).to_be_visible()

def test_launch_research_quest(page: Page):
    """Test the full user flow from input to swarm activation."""
    page.goto("http://localhost:5173")
    
    # Input a research goal
    search_input = page.get_by_placeholder("Ask about roles, skills, or salary trends in India...")
    search_input.fill("E2E Test: Java Roles in Bangalore")
    
    # Click launch
    page.get_by_role("button", name="Launch Quest").click()
    
    # Verify the Live Swarm Map appears
    expect(page.get_by_text("Live Swarm Map")).to_be_visible()
    
    # Verify the graph nodes are rendered (React Flow)
    # Each node has a 'data-id' or text label
    expect(page.get_by_text("Goal Analysis")).to_be_visible()
    expect(page.get_by_text("Initialization")).to_be_visible()

def test_tab_switching(page: Page):
    """Verify navigation between Dashboard and Technical Blueprint."""
    page.goto("http://localhost:5173")
    
    # Click Blueprint tab
    page.get_by_role("button", name="Technical Blueprint").click()
    
    # Check for Blueprint content
    expect(page.get_by_text("The LangGraph Orchestrator")).to_be_visible()
    expect(page.get_by_text("Semantic Cache")).to_be_visible()
    
    # Switch back
    page.get_by_role("button", name="Dashboard").click()
    expect(page.get_by_text("Launch an Autonomous Swarm")).to_be_visible()
