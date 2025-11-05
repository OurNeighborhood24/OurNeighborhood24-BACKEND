
## 테이블 정의
### region
region_id : bigint PK

region_code : int

region_name : varchar(255)

### user
user_id : bigint PK

region_code : bigint FK → region.region_id

email : varchar(255)

password : varchar(30)

role : enum(USER, ADMIN)

### notification
notification_id : bigint PK

writer_id : bigint FK → user.user_id

title : varchar(255)

content : text

created_at : datetime

### category
category_id : bigint PK

category_name : text

### report
report_id : bigint PK

writer_id : bigint FK → user.user_id

category_id : bigint FK → category.category_id

latitude : float

longitude : float

title : varchar(255)

description : text

image_url : text

state : enum(PENDING, CHECKED, PROCESSING, COMPLETED)

### report_answer
report_answer_id : bigint PK

report_id : bigint PK, FK → report.report_id

writer_id : bigint FK → user.user_id

answer : text

state : varchar(255)

### 관계(카디널리티)
region (1) — (N) user : user.region_code → region.region_id

user (1) — (N) notification : notification.writer_id → user.user_id

user (1) — (N) report : report.writer_id → user.user_id

category (1) — (N) report : report.category_id → category.category_id

report (1) — (0..1) report_answer : report_answer.report_id → report.report_id

(report 당 답변 최대 1개로 보임 — 복합 PK에 report_id 포함)

### 카테고리(한·영 매핑)
가로정비 → Street Maintenance

공원녹지 → Parks and Green Spaces

교통-불법주차 → Traffic – Illegal Parking

교통-장애인주차구역위반 → Traffic – Disabled Parking Violation

교통-거주자주차구역위반 → Traffic – Residential Parking Violation

교통-기타 → Traffic – Others

도로 → Road Infrastructure

소방안전 → Fire Safety

청소·쓰레기(무단투기) → Sanitation – Illegal Waste Disposal

청소·기타 → Sanitation – Others

치산·재해 → Flood Control and Disaster Prevention

환경 → Environment

보건 → Public Health

주택 → Housing

범죄 → Crime

## 엔드포인트 목록

| 도메인          | 설명           | 메서드    | 경로                               | 권한        |
| ------------ | ------------ | ------ | -------------------------------- |-----------|
| User         | 회원가입         | POST   | /users/register                  | Anonymous |
| User         | 지역 목록 조회     | GET    | /users/regions                   | Anonymous |
| User         | 본인 조회        | GET    | /users                           | User      |
| User         | 지역 설정 변경     | PATCH  | /users/my/region                 | User      |
| Auth         | 로그인          | POST   | /auth/login                      | Anonymous |
| Auth         | 토큰 재발급       | POST   | /auth/reissue                    | User      |
| Auth         | 로그아웃         | DELETE | /auth/logout                     | User      |
| Report       | 신고 이미지 업로드   | POST   | /reports/images                  | User      |
| Report       | 카테고리 목록 조회   | GET    | /reports/categories              | Anonymous |
| Report       | 신고하기         | POST   | /reports                         | User      |
| Report       | 신고 조회(지도)    | GET    | /reports/map                     | Anonymous |
| Report       | 내 신고 조회      | GET    | /reports/my                      | User      |
| Report       | 내 신고 삭제      | DELETE | /reports/{report-id}             | User      |
| Report       | 내 신고 수정      | PATCH  | /reports/{report-id}             | User      |
| Report       | 신고 목록 조회     | GET    | /reports                         | Anonymous      |
| Report       | 신고 상태 전환하기   | PATCH  | /reports/{report-id}/state       | Admin     |
| Report       | 신고 응답하기      | POST   | /reports/{report-id}/answer      | Admin     |
| Report       | 응답한 신고 목록 조회 | GET    | /reports/answers                 | Admin     |
| Notification | 공지 등록        | POST   | /notifications                   | Admin     |
| Notification | 공지 수정        | PATCH  | /notifications/{notification-id} | Admin     |
| Notification | 공지 삭제        | DELETE | /notifications/{notification-id} | Admin     |
| Notification | 공지 조회        | GET    | /notifications                   | Anonymous |
