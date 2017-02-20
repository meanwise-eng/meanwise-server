# Authentication

Official documentation for Meanwise - **[Authentication](https://github.com/meanwise-eng/meanwise-server/tree/master/custom_auth)**.

#### 1. For normal registration - Django way
* **Request URL:**

    `POST` `/api/v4/custom_auth/user/register/` 


* **Parameters:**

Parameter | Type | Required Field | 
:------------: | :-------------: | :------------: | 
Username | String | ✓ 
 Email| String | ✓
 Password | String | ✓
 First Name | String | ✓
 Middle Name | String | ✕ 
 Last Name | String | ✕ 
 Profession | Professsion Object| ✓
 Skills | List Field | ✓
 Interests | List Field | ✓
 Invite code | String | ✓
 City | String | ✕
 Profile Phtoto | Image | ✕
 Cover Photo | Image | ✕
 Bio | String | ✕
 DOB | Date Field | ✕
 Profile Story Title | String | ✕
 Profile Story Description | String | ✕
 

* **Logic:**

    Handle Registering of user for normal django flow. Capture all user information at one go. For each user generate auth token and use the same to authorize further api calls.
    
* **Request:**

```javascript
{   
    "register":
    {
        "username": "testuser11@test.com",
        "email": "testuser11@test.com",
        "password": "testpass123"
        "first_name": "testfname11",
        "last_name": "testlname11",
        "profession": 1,
        "skills": [1,2],
        "interests": [1,2],
        "invite_code": "REALPEOPLE",
        "dob": "2000-10-10",
        "profile_story_title": "profile story title 11",
        "profile_story_description": "profile story description 11",
        "cover_photo": "./Pictures/6859429-beach-wallpaper.jpg",
        "profile_photo": "./Pictures/6859429-beach-wallpaper.jpg"
    }
}
```


* **Response:**

```javascript
{
    "error": "",
    "results": {
        "auth_token": "e1d54bcce09832b9216088f1603de66f6eae05f1",
        "user": 37,
        "userprofile": 34
    },
    "status": "success"
}
```

<br/>

#### 2. Facebook Signup
* **Request URL:** 

    `POST` `/api/v4/custom_auth/user/register/` 

* **Parameters:**

Parameter | Type | Required Field | 
:------------: | :-------------: | :------------: | 
Username | String | ✓ 
 Email| String | ✓
 Facebook Token | String | ✓
 Password | String | ✓
 First Name | String | ✓
 Middle Name | String | ✕ 
 Last Name | String | ✕ 
 Profession | Professsion Object| ✓
 Skills | List Field | ✓
 Interests | List Field | ✓
 Invite code | String | ✓
 City | String | ✕
 Profile Phtoto | Image | ✕
 Cover Photo | Image | ✕
 Bio | String | ✕
 

* **Logic:**
    
    Handle Registering of user for facebook flow. Capture all user information at one go. For each user generate auth token and use the same to authorize further api calls.
    
* **Request:** 

```javascript

{
    "register": {
        "username": "testuser8@test.com", 
        "email": "testuser8@test.com",
        "facebook_token": "fbtokeneight",
        "first_name": "testfname8", 
        "profession": 1,
        "skills": [1,2],
        "interests": [1,2]
    }
}
```
    
* **Response:**

```javascript
{   
    "auth_token": "63cd2dda1508e2bcfe15550b53930f7792598e84",
    "user": 13,
    "userprofile": 9
}
```

<br/>

#### 3. Retrieve auth token

* **Request URL:**

    `POST` `/api/v4/custom_auth/api-token-auth/` 

* **Parameters:**

Parameter | Type | Required Field 
:------------: | :-------------: | :------------: 
Username | String | ✓ 
Password | String | ✓

* **Logic:**

    To retrieve user token given username and password.
    
* **Request:**

```javascript
{
    "username": "testuser5@test.com",
    "password": "testpassfive"
}
```
    
* **Response:**

```javascript
{
    "token": "93deff3e4c04e5f2ee1349035fd7637bb4df7aa0"
}
```

<br/>

#### 4. Verify Email.

* **Request URL:** 

    `POST` `/api/v4/custom_auth/user/verify/` 

* **Parameters:**

Parameter | Type | Required Field 
:------------: | :-------------: | :------------: 
Email | String | ✓ 

* **Logic:**

    Checks if the email exists or not.
    
* **Request:**

```javascript
{
    "email": "testuser5@test.com"
}
```

* **Response:**

```javascript
{
    "exists": "true"
}
```
</br>

#### 5. Fetch token and user id using email and password

* **Request URL:**

	`POST` `/api/v4/custom_auth/fetch/token/`
	
* **Paramenters:**

Parameter | Type | Required Field 
:------------: | :-------------: | :------------: 
Email | String | ✓ 
Password | String | ✓

* **Logic:**

	Fetches a User's token and user id using their email id and password.
	
* **Request:**

```javascript
{
    "email": "testuser8@test.com",
    "password": "P@ssword123!"
}
```

* **Response:**

```javascript
{
    "status": "success",
    "result": {
        "user_id": 13,
        "token": "63cd2dda1508e2bcfe15550b53930f7792598e84"
    },
    "error": ""
}

```