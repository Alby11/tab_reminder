import json
import urllib.request
import os

# Lambda function that handles incoming API requests and triggers a GitHub action
def lambda_handler(event, context):
    # Log the received payload to CloudWatch for debugging purposes
    print("Received Event:", json.dumps(event))

    # Extract the "body" from the event, which contains the main payload of the request
    body = event.get("body")
    if not body:
        # If no body is present, return an error response
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON body in event"})
        }

    # Attempt to parse the JSON body
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        # If parsing fails, return an error response
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON body in event"})
        }

    # Extract the "title" and "url" from the parsed payload, with default values if not present
    title = payload.get("title", "No Title")
    url = payload.get("url", "No URL")

    # Define the GitHub API URL where a repository dispatch event will be triggered
    github_url = "https://api.github.com/repos/Alby11/tab_reminder/dispatches"

    # Retrieve the GitHub Personal Access Token from the environment variables
    github_token = os.getenv('GITHUB_TOKEN', None)

    # If the GitHub token is not set, return an error response
    if not github_token:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "GITHUB_TOKEN not set in environment variables"})
        }

    # Set up headers for the GitHub API request, including authorization and content type
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.everest-preview+json"
    }

    # Prepare the data for the POST request, including the event type and client payload
    data = json.dumps({
        "event_type": "reminder_triggered",
        "client_payload": {
            "title": title,
            "url": url
        }
    }).encode("utf-8")

    # Create the request object with the specified URL, headers, and data
    req = urllib.request.Request(github_url, data=data, headers=headers, method="POST")

    # Send the request to GitHub API and handle possible outcomes
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()  # Get the response status code
            response_body = response.read().decode('utf-8')  # Read and decode the response body

        # Return the status code and response body as a success message
        return {
            "statusCode": status_code,
            "body": response_body
        }
    # Handle HTTP errors and return an error response with the status code and reason
    except urllib.error.HTTPError as e:
        return {
            "statusCode": e.code,
            "body": json.dumps({"error": f"HTTP Error {e.code}: {e.reason}"})
        }
    # Handle any other exceptions that might occur
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
