# Profile

Here is the link to [Meanwise Profile app](https://github.com/meanwise-eng/meanwise-server/tree/master/userprofile). 

## URL

#### 1.`/api/v4/user/userprofile/<user_id>` `GET | POST`


* **Parameters:**
  - id
  - username
  - first_name
  - last_name
  - profile_pic
  - profession
  - location(city, country)
  - summary
  - skills
  - date of birth
  - bio
  - video (introduction)
  - profile_views(count-field of profile views)
  - connections(Array of objects)

* **Logic:** `Authentication Required`
  
    - Return user's profile. Authentication is required for this view as all the details related to user's profile are public but can be viewed only to user who has Meanwise account.


* **Response:**

`GET REQUEST`
```json
{
  "status": "HTTP-GET 200 OK",
  "response": {
        "id": "12345dfgghjjn",
    "username": "grover",
        "first_name": "Punit",
        "last_name": "Grover",
        "profile_pic": "image-id",
        "cover_pic": "photo-id",
        "profession": {
          "data": [
              {
                  "id": "2313rg5465",
                    "text": "Software Engineer",
                    "slug": "software-engineer",
                    "created_on": "some-date",
                    "last_updated": "some-date",
                    "searchable": "False",
                }
            ]
        },
        "location": {
          "city": "New Delhi",
            "country": "India"
        },
        "summary": "some-text",
        "skills": {
          "data": [
              {
                  "id": "23434rytutu",
                    "text": "#Django",
                    "lower": "django",
                    "slug": "slug",
                    "created_on": "some-date",
                    "last_updated": "some-date",
                    "searchable": "True",
                },
                {
                  "id": "123423434rytutu",
                    "text": "Java",
                    "lower": "java",
                    "slug": "slug",
                    "created_on": "some-date",
                    "last_updated": "some-date",
                    "searchable": "False",
                }
            ]
        },
        "DOB": "some-date",
        "interest": {
          "data": [
              {
                  "id": "123343rfvvgtgv",
                    "name": "#Science",
                    "slug": "Science",
                    "description": "some-description",
                    "created_on": "somedate",
                    "modified_on": "some-date",
                    "publiched": "some-date",
                    "cover_photo": "coverphoto-id",
                    "color_code": "#333"
                },
                {
                  "id": "1256743rfvvgtgv",
                    "name": "Technology",
                    "slug": "Technology",
                    "description": "some-description",
                    "created_on": "somedate",
                    "modified_on": "some-date",
                    "publiched": "some-date",
                    "cover_photo": "coverphoto-id",
                    "color_code": "#333"
                }
            ]
        },
        "bio": "some-text",
        "video": "video-id",
        "profile_views": "300",
        "connections": ["object1", "object2"],
    "success": "Profile info"
  } 
}
```
* **Request Sent:**

```json
{
  "username": "grover",
    "first_name": "Punit",
    "last_name": "Grover",
    "profile_pic": "image-id",
    "cover_pic": "photo-id",
    "profession": ["Software Engineer"],
    "location": {
        "city": "New Delhi",
        "country": "India"
    },
    "summary": "some-text",
    "skills": ["#skill-objects", "object2"],
    "DOB": "some-date",
    "interest": ["#interestobjects", "object2"],Rangpur Pahadi 
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

#### 2.`/api/v4/profession` `GET`


* **Parameters:**

  - id
    - text
    - slug
    - created_on
    - last_updated
    - searchable
    

* **Logic:**
  
    List all the professions.
    
* **Response**

```json
{
  "status": "HTTP-GET 200 OK",
  "response": {
      "profession": {
        "data": [
            {
            "id": "2313rg5465",
            "text": "Software Engineer",
            "slug": "software-engineer",
            "created_on": "some-date",
            "last_updated": "some-date",
            "searchable": "False",
            },
            {
            "id": "23121g5465",
            "text": "Front-end Developer",
            "slug": "Front-end-developer",
            "created_on": "some-date",
            "last_updated": "some-date",
            "searchable": "False",
            }
          ]
        }
  }
}
```

<br/>

#### 3.`/api/v4/skills` `GET`


* **Parameters:**

  - id
    - text
    - lower
    - slug
    - created_on
    - last_updated
    - searchable
    

* **Logic:**
  
    List all the skills.
    
* **Response**

```json
{
  "status": "HTTP-GET 200 OK",
  "response": {
      "skills": {
          "data": [
              {
                  "id": "23434rytutu",
                    "text": "#Django",
                    "lower": "django",
                    "slug": "slug",
                    "created_on": "some-date",
                    "last_updated": "some-date",
                    "searchable": "True",
                },
                {
                  "id": "123423434rytutu",
                    "text": "Java",
                    "lower": "java",
                    "slug": "slug",
                    "created_on": "some-date",
                    "last_updated": "some-date",
                    "searchable": "False",
                }
            ]
        }
    }
}
```


<br/>

#### 4.`/api/v4/skills` `GET`


* **Parameters:**

  - id
    - name
    - slug
    - description
    - created_on
    - modified_on
    - published
    - cover_photo
    - color_code
    

* **Logic:**
  
    List all the interests.
    
* **Response**

```json
{
  "status": "HTTP-GET 200 OK",
  "response": {
      "interest": {
          "data": [
              {
                  "id": "123343rfvvgtgv",
                    "name": "#Science",
                    "slug": "Science",
                    "description": "some-description",
                    "created_on": "somedate",
                    "modified_on": "some-date",
                    "publiched": "some-date",
                    "cover_photo": "coverphoto-id",
                    "color_code": "#333"
                },
                {
                  "id": "1256743rfvvgtgv",
                    "name": "Technology",
                    "slug": "Technology",
                    "description": "some-description",
                    "created_on": "somedate",
                    "modified_on": "some-date",
                    "publiched": "some-date",
                    "cover_photo": "coverphoto-id",
                    "color_code": "#333"
                }
            ]
        }
    }
}
```