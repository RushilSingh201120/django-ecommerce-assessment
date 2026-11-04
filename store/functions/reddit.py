
import requests


def get_reddit_posts(subreddit="python"):
    # Build the URL for the subreddit's JSON feed
    url = f"https://www.reddit.com/r/{subreddit}/.json"

    # Include the required User-Agent header
    headers = {
        "User-Agent": "DjangoEcommerceApp/1.0"
    }

    try:
        # Make the GET request
        response = requests.get(url, headers=headers, timeout=15)

        # Handle unsuccessful responses
        if response.status_code != 200:
            print(f"Failed to fetch Reddit data: {response.status_code}")
            return []

        # Parse the JSON response
        data = response.json()

        posts = []

        # Extract the post details
        for item in data["data"]["children"]:
            post = item["data"]

            posts.append({
                "title": post["title"],
                "author": post["author"],
                "url": post["url"]
            })

        return posts

    except (requests.RequestException, ValueError, KeyError) as error:
        print(f"Error retrieving Reddit posts: {error}")
        return []