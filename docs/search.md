# Search

Official documentation for Meanwise Search application.

#### 1. Search for Posts:

* **Logic:**
	
    Use interest_name (channel  name) and post_text (text of the post) for searching.
    
* **Request URL:** `GET`

	Request URL may look like :
	 `/api/v4/search/post/interest_name=%22music%22&post_text=%22test%20post%20one%22`


* **Response:**

```javascript
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "post_text": "test post one",
            "interest_name": "music",
            "text": null,
            "id": "1"
        }
    ]
}
```

#### 2. Search for User:

* **Logic:**
	
    Search for userprofile.
    
    * A Skill  is mapped to skills_text, can use comma seperated values, e.g. python,django.
    
* **Request URL:** `GET`

	Request URL may look like:
	
    ```
    /api/v4/search/userprofile/?skills_text=python&username=testuser2
    ```
    
* **Response:**

```javascript
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "13",
            "first_name": "fname2",
            "skills_text": [
                "python",
                "django"
            ],
            "username": "testuser2",
            "last_name": "lname2"
        }
    ]
}
```