# Profile

Official documentation of [Meanwise Profile app](https://github.com/meanwise-eng/meanwise-server/tree/master/userprofile). 



#### 1. Profession Call:

* **Request URL:**

  `GET` `/api/v4/profession/`


* **Logic:** `Authentication Required`
  
    List all the professions. Authorization token will be required in the request header while sending a request to the URL.


* **Response:**

```javascript
{
    "count": 2,
    "next": null,
    "previous": null,
    "results":[
        {
            "id": 1,
            "text": "IT",
            "slug": "IT",
            "created_on": "2016-09-15T12:13:26.916938Z",
            "last_updated": "2016-09-15T12:13:26.916964Z",
            "searchable": true
        },
        {
          "id": 2,
            "text": "athlete",
            "slug": "athlete",
            "created_on": "2016-09-15T12:13:44.737235Z",
            "last_updated": "2016-09-15T12:13:44.737299Z",
            "searchable": true
        }
    ]
}
  
```


<br/>

#### 2. Skill call:

* **Request URL:**

  `GET` `/api/v4/skill/`
    

* **Logic:** `Authentication Required`
  
    List all the skills. Authorization token will be required in the request header while sending a request to the URL.
    
* **Response**

```javascript
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "text": "python",
            "lower": "python",
            "slug": "python",
            "created_on": "2016-09-15T12:13:54.964201Z",
            "last_updated": "2016-09-15T12:13:54.964201Z",
            "searchable": true
        },    
        {   
            "id": 2,
            "text": "django",
            "lower": "django",
            "slug": "django",
            "created_on": "2016-09-15T12:14:14.290444Z",
            "last_updated": "2016-09-15T12:14:14.290471Z",
            "searchable": true
        }
   ]
}
```

<br/>

#### 3. Interest call:

* **Request URL:**

  `GET` `/api/v4/skills/` 

* **Logic:** `Authentication Required`
  
    List all the interests. Authorization token will be required in the request header while sending a request to the URL.
    
* **Response**

```javascript
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "sports",
            "slug": "sports",
            "description": "sports",
            "created_on": "2016-09-15T12:11:06.377205Z",
            "modified_on":"2016-09-15T12:11:06.377234Z",
            "published": false,
            "cover_photo": "https://squelo.com/media/interest_photos/IMG_20140525_164408761.jpg",
            "color_code": "asda"
        },  
        {
            "id": 2,
            "name": "music",
            "slug": "music",
            "description": "music",
            "created_on": "2016-09-15T12:12:18.297699Z",
            "modified_on": "2016-09-15T12:12:18.297726Z",
            "published": false,
            "cover_photo": "https://squelo.com/media/interest_photos/IMG_20140218_215136954.jpg",
            "color_code": "wrw"
        }
    ]
}
```

<br/>

#### 4. Userprofile:

* **Request URL:**
  
    `GET` `/api/v4/user/userprofile/`
    
* **Logic:** `Authentication Required`

  List the profile info of the user. Authorization token will be required in the request header while sending a request to the URL.
    
* **Response:**

``` javascript
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "facebook_token": "",
            "username": "testuser1",
            "first_name": "tfname1",
            "middle_name": "tmidname1",
            "last_name": "tlname1",
            "city": "bangalore",
            "profile_photo": "http://127.0.0.1:49100/http:/127.0.0.1:49100/media/profile_photos/IMG_20140321_104523179.jpg",
            "cover_photo": "http://127.0.0.1:49100/http:/127.0.0.1:49100/media/cover_photos/IMG_20140329_135903539.jpg",
            "bio": "Test bio",
            "created_on": "2016-09-15T12:17:13.786931Z",
            "last_updated": "2016-09-15T12:17:13.786953Z",
            "user": 2,
            "profession": 1,
            "skills": [1,2],
            "interests": [1,2]
        }
   ]
}
```
<br/>

#### 5. Skill call with pagination:

* **Request URL:**

  `GET` `/api/v4/skill/?page=<page_number>`
    
* **Logic:** `Authentication Required`

  List out all the skills with pagination. Authorization token will be required in the request header while sending a request to the URL.
    
* **Response:**

```javascript
{
    "num_pages": 1,
    "results": [
        {
            "id": 2,
            "photo": "/media/interest_photos/IMG_20140218_215136954.jpg"
        },
        {
            "id": 1,
            "photo": "/media/interest_photos/IMG_20140525_164408761.jpg"
        }
    ],
    "error": "",
    "status": "success"
}
```

<br/>

#### 6. Interest call with pagination:

* **Request URL:**

  `GET` `/api/v4/interest/?page=<page_number>`
    
* **Logic:** `Authentication Required`

  List out all the interests with pagination. Authorization token will be required in the request header while sending a request to the URL.
    
* **Response:**

```javascript
{
    "num_pages": 1,
    "results": [
        {
            "id": 2,
            "photo": "/media/interest_photos/IMG_20140218_215136954.jpg"
        },
        {
            "id": 1,
            "photo": "/media/interest_photos/IMG_20140525_164408761.jpg"
        }
    ],
    "error": "",
    "status": "success"
}
```

<br/>

#### 7. Profession call with pagination:

* **Request URL:**

  `GET` `/api/v4/profession/?page=<page_number>`
    
* **Logic:** `Authentication Required`

  List out all the professions with pagination. Authorization token will be required in the request header while sending a request to the URL.
    
* **Response:**

```javascript
{
    "num_pages": 1,
    "results": [
        {
            "id": 1,
            "text": "IT"
        },
        {
            "id": 2,
            "text": "athlete"
        }
    ],
    "error": "",
    "status": "success"
}
```
</br>

#### 8. User Profile update

* **Request URL:**

	`PATCH` `/api/v4/user/<user_id>/userprofile/`
	
* **Parameters:**

Parameter | Type
:------------: | :-------------:
Username | String 
 Email| String
 Password | String
 First Name | String
 Middle Name | String 
 Last Name | String 
 Profession | Professsion Object
 Skills | List Field
 Interests | List Field
 Invite code | String
 City | String
 Profile Phtoto | Image
 Cover Photo | Image
 Bio | String
 DOB | Date Field
 Profile Story Title | String
 Profile Story Description | String

	
* **Logic:** `Authentication Required`

	Updates a user profile based on the parameters that one wants to update. Authorization token will be required for updating profile. Since its a `PATCH` request then only the updated paramenters will be sent in the request
	
* **Request:**

```javascript
{
	"profile_photo": "/Pictures/mobile/IMG_20140310_195139094.jpg", 
	"bio": "test bio 11", 
	"professphone": "+11234567891", 
	"dob": "1980-10-30", 
	"cover_photo": "/Pictures/mobile/IMG_20140310_195139094.jpg"
	"profession": 1, 
	"city": "bangalore", 
	"first_name": "newfnameagain", 
	"last_name": "newlnameagain"
}
```

* **Response:**

```javascript

{
	"error": "",
	"status": "success",
	"results": {
		"id": 7,
		"user_id": 11,
		"email": "testuser5@test.com",
		"username": "",
		"profile_photo": "/media/profile_photos/IMG_20140310_195139094_qSzEtGF.jpg",
		"cover_photo": "/media/cover_photos/IMG_20140310_195139094_38xc5sd.jpg",
		"profile_photo_small": "/media/profile_photos/IMG_20140310_195139094_qSzEtGF.jpg..jpg",
		"first_name": "newfnameagain",
		"last_name": "newlnameagain",
		"bio": "test bio 11",
		"skills": [
			{
				"id": 1,
				"name": "python"
			},
			{
				"id": 2,
				"name": "django"
			}
		],
		"profession": 1,
		"user_profession": {
			"id": 1,
			"name": "IT"
		},
		"interests": [
			{
				"id": 1,
				"name": "sports"
			},
			{
				"id": 2,
				"name": "music"
			}
		],
		"intro_video": null,
		"phone": "+11234567891",
		"dob": "1980-10-30",
		"profile_story_title": null,
		"profile_story_description": null
	}
}
```
</br>

#### 9. UserProfile detail using given user id

* **Request URL:**

	`GET` `/api/v4/user/<user_id>/userprofile/`
	
* **Logic:** `Authetication Required`

	List the details of a user profile using their user id. Authorization token will be required while sending the request.
	
* **Response:**

```javascript
{
	"status": "success",
	"results": {
		"id": 7,
		"user_id": 11,
		"email": "testuser5@test.com",
		"username": "",
		"profile_photo": null,
		"cover_photo": "/media/cover_photos/IMG_20140310_195139094_rUSTf0c.jpg",
		"profile_photo_small": "",
		"first_name": "testfname5",
		"last_name": "",
		"bio": null,
		"skills": [
			{
				"id": 1,
				"name": "python"
			},
			{
				"id": 2,
				"name": "django"
			}
		],
		"profession": {},
		"interests": [
			{
				"id": 1,
				"name": "sports"
			},
			{
				"id": 2,
				"name": "music"
			}
		],
		"intro_video": null,
		"phone": "+11234567891",
		"dob": "1980-10-30"
	},
	"error": ""
}
```
	