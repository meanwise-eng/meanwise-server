# Post

Official documentation for Meanwise - **[Post](https://github.com/meanwise-eng/meanwise-server/tree/master/post)**

#### 1. Post a 'Post':
* **Request URL:**

	`POST` `/api/v4/user/user_id/posts`
    
* **Parameters:**

Parameter | Type | Required Field | 
:------------: | :-------------: | :------------: | 
 interest | Interest Object | ✓ 
 image | Image | ✕
 video | File | ✕
 text | String | ✕
 poster | User object | ✓
 tags | Hashtags | ✕
 liked_by | User's object | ✕
 video_height | Integer | ✕
 video_width | Integer | ✕
 video_thumbnail | Image | ✕
 created_on | Datetime | auto
 modified_on | Datetime | auto
 

* **Logic:** `Authorization Token Required`
 
 Let's a user to post a story. Token would be required in request header.
 

* **Request:**

```javascript
{
	"text": "text post dec22", 
    "interest": 1
}

```

* **Response:**

```javascript
{
	"status": "success",
    "error": "",
    "results": {
    	"id": 2,
        "image": null,
        "video": null,
        "text": "text post dec22",
        "is_deleted": false,
        "video_height": null,
        "video_width": null,
        "video_thumbnail": null,
        "created_on": "2016-12-22T09:11:01.777737Z",
		"modified_on": "2016-12-22T09:11:01.777763Z",
		"interest": 1,
		"poster": 17,
		"liked_by": []
    }
}
```
<br/>

#### 2. List user's posts:
* **Request URL:**

	`GET` `/api/v4/user/user_id/posts/`
    
* **Logic:** `Authentication Required`

	List all the post of users. Authorization token will be required in the request header while sending the request.
    
* **Response:**

```javascript
{
	"error": "",
    "results": [
    	{
        	"id": 1,
            "text": "test post one",
            "user_id": 9,
            "num_likes": 2,
            "num_comments": 1,
            "interest_id": 2,
            "user_firstname": "fname2",
            "user_lastname": "lname2",
            "user_profile_photo": "/media/profile_photos/6859429-beach-wallpaper_HwW9VbE.jpg",
			"user_cover_photo": "/media/cover_photos/lunamore-noch-lyudi-serfing_XmPS2Ta.jpg",
			"user_profile_photo_small": "/media/profile_photos/6859429beach-wallpaper_HwW9VbE.jpg..jpg",
			"user_profession": {
					"id": 1,
                    "name": "IT"
             	},
			"image_url": "",
            "video_url": "",
            "video_thumb_url": "",
            "resolution": null
       },
       {
       		"id": 2,
            "text": "text post dec22",
            "user_id": 17,
            "num_likes": 0,
            "num_comments": 0,
			"interest_id": 1,
			"user_firstname": "testfname10",
			"user_lastname": "",
			"user_profile_photo": "/media/profile_photos/luna-more-noch-lyudiserfing_H81m58R.jpg",
			"user_cover_photo": "/media/cover_photos/6859429-beachwallpaper_UrUDeN4.jpg",
			"user_profile_photo_small": "/media/profile_photos/luna-morenochlyudiserfing_H81m58R.jpg..jpg",
            "user_profession": {},
            "image_url": "",
            "video_url": "",
            "video_thumb_url": "",
            "resolution":null
       }
   ],
   "status": "success"
}
```

<br/>

#### 3. Delete a post:
* **Request URL:**

	`DELETE` `/api/v4/user/user_id/posts/post_id/`
    
* **Logic:** `Authentication Token Required`
	
    Deletes a post by sending a `DELETE` request with the user_id and post_id in the URL with the authorization token in the header.
    
* **Response:**

```javascript
{
	"status": "success",
    "results": "Succesfully deleted.",
    "error": ""
}
```

</br>