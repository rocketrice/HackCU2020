import tweepy

def main():
    twitter_auth_keys = {
        "consumer_key": "quRVTzQpkAH8HnpoSkZbIdTxv",
        "consumer_secret": "Efew2bIFEer0UrYGMVa2TSfAwpMmFoXks7phyfnFyYxnyfRXc2",
        "access_token": "1231384108003024897-OLXRdh0vXMoaGPsaO68lcAX8GiyXeT",
        "access_token_secret": "iVzR5u9zcdV0g1fCIGcnEaukFOfKroPAeH6VrKw7yx0mH"
    }

    auth = tweepy.OAuthHandler(
        twitter_auth_keys['consumer_key'],
        twitter_auth_keys['consumer_secret']
    )
    auth.set_access_token(
        twitter_auth_keys['access_token'],
        twitter_auth_keys['access_token_secret']
    )
    api = tweepy.API(auth)

    #tweet = "Another day, another #scifi #book and a cup of #coffee"
    #status = api.update_status(status=tweet)

    # Upload image
    media = api.media_upload("coffee.jpg")

    # Post tweet with image
    tweet = "Nae Naed #hackcu"
    post_result = api.update_status(status=tweet, media_ids=[media.media_id])


if __name__ == "__main__":
    main()