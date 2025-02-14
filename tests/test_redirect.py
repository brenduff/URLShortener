import os
import json
import pytest
from main import app, generate_short_url, shortened_urls

# Pytest fixture to set up the test client
@pytest.fixture
def client():
    # Enable testing mode
    app.testing = True

    # Clear any previously stored URLs and remove the urls.json file if it exists
    shortened_urls.clear()
    if os.path.exists("urls.json"):
        os.remove("urls.json")

    with app.test_client() as client:
        yield client

    # Cleanup after test runs
    if os.path.exists("urls.json"):
        os.remove("urls.json")

def test_index_get(client):
    """
    Test that a GET request to the index route returns a 200 status code.
    """
    response = client.get('/')
    assert response.status_code == 200
    # Optionally, you might check for some expected content if you have a known index.html template

def test_create_short_url(client):
    """
    Test that posting a URL creates a new shortened URL.
    """
    test_url = "http://example.com"
    response = client.post('/', data={'url': test_url})

    # Check that the response contains the expected message
    assert b"Shortened URL:" in response.data

    # Verify that the global dictionary has stored the URL
    assert any(url == test_url for url in shortened_urls.values())

def test_redirect_to_url(client):
    """
    Test that accessing a valid short URL redirects to the original URL.
    """
    test_url = "http://example.com"
    # Create a short URL via POST
    client.post('/', data={'url': test_url})

    # Find the generated short URL key for the test_url
    short_url = None
    for key, value in shortened_urls.items():
        if value == test_url:
            short_url = key
            break
    assert short_url is not None, "Short URL was not created."

    # Simulate a GET request to the shortened URL
    response = client.get(f'/{short_url}')
    # Check that the response is a redirect (HTTP 302)
    assert response.status_code == 302
    # Verify that the Location header matches the original URL
    assert response.headers['Location'] == test_url

def test_invalid_short_url(client):
    """
    Test that accessing an invalid/unknown short URL returns a 404 error.
    """
    response = client.get('/nonexistent')
    assert response.status_code == 404
    assert b"URL not found" in response.data

def test_generate_short_url_length():
    """
    Test that generate_short_url returns a string of length 6.
    """
    short_url = generate_short_url()
    assert isinstance(short_url, str)
    assert len(short_url) == 6

def test_generate_short_url_uniqueness():
    """
    Test that multiple calls to generate_short_url produce unique values.
    """
    urls = {generate_short_url() for _ in range(100)}
    assert len(urls) == 100
