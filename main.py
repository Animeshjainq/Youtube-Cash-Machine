import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# Set up the OAuth2 credentials
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret.json"  # Your client secrets file from the Google Developer Console

# Authenticate and build the service
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes
)
credentials = flow.run_local_server()  # Use run_local_server instead of run_console
youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

# Retrieve videos from the source channel's uploads playlist
source_channel_id = "UCcYzLCs3zrQIBVHYA1sK2sw"
playlist_items = youtube.playlistItems().list(
    part="snippet",
    maxResults=50,  # Adjust as needed
    playlistId=f"UU{source_channel_id[2:]}",
).execute()

# Upload videos to the destination channel
destination_channel_id = "UCB_IeX5Kr05rksGY2MfS7gg"
for item in playlist_items["items"]:
    video_id = item["snippet"]["resourceId"]["videoId"]

    try:
        # Get video details
        video_response = youtube.videos().list(part="snippet", id=video_id).execute()
        video_details = video_response["items"][0]["snippet"]

        # Prepare video upload request
        request_body = {
            "snippet": {
                "title": video_details["title"],
                "description": video_details["description"],
                "tags": video_details.get("tags", []),
                "categoryId": video_details["categoryId"],
                "thumbnails": video_details.get("thumbnails", {}),
            },
            "status": {
                "privacyStatus": "public",  # Change to "public" or "unlisted" as needed
            },
            "fileDetails": {
                "url": "https://drive.google.com/file/d/1bdVu8sm-9X51gbVSiiDCRmmAM-D-4fUr/view?usp=drive_link"  # Replace with the actual URL of the video file
            }
        }

        # Execute the video insert request
        upload_response = youtube.videos().insert(
            part="snippet,status,fileDetails",
            body=request_body
        ).execute()

        print(f"Video uploaded: https://www.youtube.com/watch?v={upload_response['id']}")

    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")

    # Implement rate limiting or scheduling logic if needed
