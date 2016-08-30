## API end points


#### Company, Jobs and Pages App URLs

|  URL | REQUEST METHOD  | DESCRIPTION|
|---|---|---|
|  `/api_v3/company/`    | GET |  List of all companies |
|  `/api_v3/company/<company_slug>/ ` | GET/PUT/DEL |  Specific company (company_slug) |
| `/api_v3/<company_slug>/`  | CRUD  |CompanyProfile   |
| `/api_v3/<company_slug>/locations/`  | CRUD  |  CompanyLocation |
| ` /api_v3/jobs/list/`  | GET/POST  | Create job, List company jobs  |
| `/api_v3/jobs/<company_slug>/<job_slug>/ `  | GET/PUT/DEL  |  Detail of job, endpoint to modify |
| ` /api_v3/jobs/<company_slug>/<job_slug>/apply/ `  |  POST |  Apply job endpoint |
| ` /api_v3/jobs/<username>/recommendations/ `  | GET  |   Returns recommended (not ai) jobs |
| ` /api_v3/pages/<company_slug>/   `  |  GET/POST  | Creation/get endpont for Page  |
| `/api_v3/pages/<company_slug>/<page_slug>/ `  |  PUT/DEL |  Update/delete endpoint for Page |
|` /api_v3/pages/<company_slug>/leaders/  `   | CRUD  | Leader  |


#### Stripe App URLs
|  URL | REQUEST METHOD  | DESCRIPTION|
|---|---|---|
|  `/api_v3/stripe/current-user/`    | GET | Current User Details   |
|  `/api_v3/stripe/subscribe/`    |  GET, POST, DELETE |  Get customer or create subscription details or cancel subscription details |
|  `/api_v3/stripe/confirm/<plan>`    | GET, POST | Get subscription details if there is not then subscribe customer to a plan  |
|  `/api_v3/stripe/change/plan/`    | POST | Change Subscription Plan  |
|  `/api_v3/stripe/change/cards/`    | POST |  Add or update customer card details |
|  `/api_v3/stripe/cancel/subscription/`    | POST |  Cancel the subscription of a customer |
|  `/api_v3/stripe/event/`    | GET |  List customer events  |
|  `/api_v3/stripe/history/`    | GET |  List History details   |
|  `/api_v3/stripe/sync/history/`    | POST | Sync Customer History with Stripe API  |
|  `/api_v3/stripe/webhook/`    | POST | Webhook  |


#### Candidate Manager URLs
|  URL | REQUEST METHOD  | DESCRIPTION|
|---|---|---|
|  `/api_v3/candidate_manager/<company_slug>/<job_slug>/view_applicants/`    | POST | Apply for job   |

#### Search App URLs
|  URL | REQUEST METHOD  | DESCRIPTION|
|---|---|---|
|  `/api_v3/search/`    | GET | Get result of profile search |
|  `/api_v3/jobs/`    | POST | Grabs a list of recommended jobs based on user query |
