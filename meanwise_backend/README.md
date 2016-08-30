## API end points


#### Company App Urls

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
