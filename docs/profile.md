# Profile

Here is the link to [Meanwise Profile app](https://github.com/meanwise-eng/meanwise-server/tree/master/account_profile). 

## URL

#### `profile/<username>` `GET | POST | PUT | PATCH`


* **Parameters:**
  - username
  - first_name
  - last_name
  - profile_pic
  - profession
  - location(city, country)
  - summary
  - skills
  - age
  - bio
  - video (introduction)
  - profile_views(count-field)
  - connections(Array of objects)

* **Logic:** `Authentication Required`
	
    - Return user's profile. Authentication is required for this view as all the details related to user's profile are public but can be viewed only to user who has Meanwise account. 
    - Also a user can update his/her profile details.


* **Response:**

```json
{
	"status": "HTTP 200 OK",
	"response": {
		"access_token": "jabhjbsadfjbsadf231312",
		"username": "grover",
        "first_name": "Punit",
        "last_name": "Grover",
        "profile_pic": "image-id",
        "profession": "Software Engineer",
        "location": {
        	"city": "New Delhi",
            "country": "India"
        },
        "summary": "some-text",
        "skills": ["#Python","#Django","#some-more skills"],
        "age": "21",
        "bio": "some-text",
        "video": "video-id",
        "profile_views": "300",
        "connections": ["object1", "object2"],
		"success": "Profile info"
	}	
}
```

* **Profile Overview:** 

![alt text](https://d2gn4xht817m0g.cloudfront.net/p/product_screenshots/images/original/000/734/429/734429-a986fb24ca026a66913858db3062f79735f416db.png?1471020221 "Meanwise Profile")

![alt text](https://github.com/meanwise-eng/meanwise-server/blob/master/docs/prfle.png "Meanwise")


<br/>
