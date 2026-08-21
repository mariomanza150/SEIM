# SEIM Database Schema

Generated on: 2026-08-21 03:30:44

## accounts_academiclevel

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| code | character varying | NO |  |  |
| is_active | boolean | NO |  |  |
| ordering | integer | NO |  |  |

## accounts_allowedemaildomain

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| code | character varying | NO |  |  |
| is_active | boolean | NO |  |  |
| ordering | integer | NO |  |  |

## accounts_bankinstitution

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| code | character varying | NO |  |  |
| is_active | boolean | NO |  |  |
| ordering | integer | NO |  |  |

## accounts_googlecalendarconnection

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| google_email | character varying | NO |  |  |
| access_token | text | NO |  |  |
| refresh_token | text | NO |  |  |
| token_expiry | timestamp with time zone | YES |  |  |
| google_calendar_id | character varying | NO |  |  |
| last_synced_at | timestamp with time zone | YES |  |  |
| last_sync_error | text | NO |  |  |
| event_map | jsonb | NO |  |  |
| user_id | uuid | NO |  |  |
| imported_events | jsonb | NO |  |  |

## accounts_homeacademicprogram

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| code | character varying | NO |  |  |
| is_active | boolean | NO |  |  |
| ordering | integer | NO |  |  |
| school_id | uuid | NO |  |  |

## accounts_permission

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| name | character varying | NO |  |  |

## accounts_permission_roles

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| permission_id | bigint | NO |  |  |
| role_id | bigint | NO |  |  |

## accounts_profile

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| secondary_email | character varying | YES |  |  |
| gpa | double precision | YES |  |  |
| language | character varying | YES |  |  |
| user_id | uuid | NO |  |  |
| grade_scale_id | uuid | YES |  |  |
| date_of_birth | date | YES |  |  |
| language_level | character varying | YES |  |  |
| additional_languages | jsonb | NO |  |  |
| birthplace | character varying | NO |  |  |
| clabe | character varying | NO |  |  |
| gender | character varying | NO |  |  |
| matricula | character varying | YES |  |  |
| mobile_phone | character varying | NO |  |  |
| passport_number | character varying | NO |  |  |
| postal_code | character varying | NO |  |  |
| rfc | character varying | NO |  |  |
| academic_level_id | uuid | YES |  |  |
| bank_institution_id | uuid | YES |  |  |
| home_academic_program_id | uuid | YES |  |  |
| school_id | uuid | YES |  |  |
| unidad_id | uuid | YES |  |  |
| credits_approved_percent | numeric | YES |  |  |
| current_semester | integer | YES |  |  |
| ingress_date | date | YES |  |  |

## accounts_role

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| name | character varying | NO |  |  |

## accounts_schoolfaculty

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| code | character varying | NO |  |  |
| is_active | boolean | NO |  |  |
| ordering | integer | NO |  |  |

## accounts_unidad

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| code | character varying | NO |  |  |
| is_active | boolean | NO |  |  |
| ordering | integer | NO |  |  |

## accounts_user

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| password | character varying | NO |  |  |
| last_login | timestamp with time zone | YES |  |  |
| is_superuser | boolean | NO |  |  |
| username | character varying | NO |  |  |
| first_name | character varying | NO |  |  |
| last_name | character varying | NO |  |  |
| is_staff | boolean | NO |  |  |
| is_active | boolean | NO |  |  |
| date_joined | timestamp with time zone | NO |  |  |
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| email | character varying | NO |  |  |
| is_email_verified | boolean | NO |  |  |
| email_verification_token | character varying | YES |  |  |
| failed_login_attempts | integer | NO |  |  |
| lockout_until | timestamp with time zone | YES |  |  |
| middle_name | character varying | NO |  |  |
| mothers_last_name | character varying | NO |  |  |

## accounts_user_groups

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| user_id | uuid | NO |  |  |
| group_id | integer | NO |  |  |

## accounts_user_roles

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| user_id | uuid | NO |  |  |
| role_id | bigint | NO |  |  |

## accounts_user_user_permissions

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| user_id | uuid | NO |  |  |
| permission_id | integer | NO |  |  |

## accounts_usersession

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| session_key | character varying | NO |  |  |
| user_agent | text | NO |  |  |
| ip_address | inet | YES |  |  |
| device | character varying | NO |  |  |
| location | character varying | NO |  |  |
| is_active | boolean | NO |  |  |
| last_activity | timestamp with time zone | NO |  |  |
| user_id | uuid | NO |  |  |

## accounts_usersettings

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| theme | character varying | NO |  |  |
| font_size | character varying | NO |  |  |
| email_applications | boolean | NO |  |  |
| email_documents | boolean | NO |  |  |
| email_programs | boolean | NO |  |  |
| email_system | boolean | NO |  |  |
| inapp_applications | boolean | NO |  |  |
| inapp_documents | boolean | NO |  |  |
| inapp_comments | boolean | NO |  |  |
| profile_public | boolean | NO |  |  |
| share_analytics | boolean | NO |  |  |
| user_id | uuid | NO |  |  |
| high_contrast | boolean | NO |  |  |
| reduce_motion | boolean | NO |  |  |
| email_notification_digest | boolean | NO |  |  |
| notification_digest_frequency | character varying | NO |  |  |
| notification_digest_last_sent_at | timestamp with time zone | YES |  |  |
| email_comments | boolean | NO |  |  |
| inapp_programs | boolean | NO |  |  |
| inapp_system | boolean | NO |  |  |

## analytics_dashboardconfig

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| config | jsonb | NO |  |  |
| user_id | uuid | NO |  |  |

## analytics_metric

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| value | double precision | NO |  |  |
| calculated_at | timestamp with time zone | NO |  |  |
| report_id | uuid | NO |  |  |

## analytics_report

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| description | text | NO |  |  |
| created_by_id | uuid | YES |  |  |

## application_forms_formsteptemplate

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| name | character varying | NO |  |  |
| slug | character varying | NO |  |  |
| description | text | NO |  |  |
| step_title | character varying | NO |  |  |
| default_step_key | character varying | NO |  |  |
| schema_properties | jsonb | NO |  |  |
| required_field_names | jsonb | NO |  |  |
| ui_schema_fragment | jsonb | NO |  |  |
| required_document_type_ids | jsonb | NO |  |  |
| is_active | boolean | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |

## application_forms_formsubmission

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| responses | jsonb | NO |  |  |
| submitted_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| application_id | uuid | YES |  |  |
| program_id | uuid | YES |  |  |
| submitted_by_id | uuid | YES |  |  |
| form_type_id | bigint | NO |  |  |

## application_forms_formtype

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| name | character varying | NO |  |  |
| form_type | character varying | NO |  |  |
| description | text | NO |  |  |
| schema | jsonb | NO |  |  |
| ui_schema | jsonb | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| is_active | boolean | NO |  |  |
| created_by_id | uuid | YES |  |  |
| step_definitions | jsonb | NO |  |  |

## auth_group

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| name | character varying | NO |  |  |

## auth_group_permissions

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| group_id | integer | NO |  |  |
| permission_id | integer | NO |  |  |

## auth_permission

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| name | character varying | NO |  |  |
| content_type_id | integer | NO |  |  |
| codename | character varying | NO |  |  |

## cms_blogcategory

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| name | character varying | NO |  |  |
| slug | character varying | NO |  |  |
| description | text | NO |  |  |

## cms_blogindexpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| introduction | text | NO |  |  |
| og_image_id | integer | YES |  |  |

## cms_blogpostpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| published_date | date | NO |  |  |
| introduction | text | NO |  |  |
| body | jsonb | NO |  |  |
| author_id | uuid | YES |  |  |
| featured_image_id | integer | YES |  |  |
| og_image_id | integer | YES |  |  |

## cms_blogpostpage_categories

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| blogpostpage_id | integer | NO |  |  |
| blogcategory_id | bigint | NO |  |  |

## cms_blogposttag

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| content_object_id | integer | NO |  |  |
| tag_id | integer | NO |  |  |

## cms_cgripage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| subtitle | character varying | NO |  |  |
| introduction | text | NO |  |  |
| body | jsonb | NO |  |  |
| show_contact | boolean | NO |  |  |
| contact_name | character varying | NO |  |  |
| contact_title | character varying | NO |  |  |
| contact_email | character varying | NO |  |  |
| contact_phone | character varying | NO |  |  |
| contact_office | character varying | NO |  |  |
| featured_image_id | integer | YES |  |  |
| og_image_id | integer | YES |  |  |

## cms_convenioindexpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| introduction | text | NO |  |  |
| og_image_id | integer | YES |  |  |

## cms_conveniopage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| institution_name | character varying | NO |  |  |
| country | character varying | NO |  |  |
| city | character varying | NO |  |  |
| agreement_type | character varying | NO |  |  |
| start_date | date | YES |  |  |
| end_date | date | YES |  |  |
| introduction | text | NO |  |  |
| body | jsonb | NO |  |  |
| available_for_students | boolean | NO |  |  |
| available_for_faculty | boolean | NO |  |  |
| available_for_research | boolean | NO |  |  |
| institution_website | character varying | NO |  |  |
| institution_logo_id | integer | YES |  |  |
| og_image_id | integer | YES |  |  |

## cms_conveniopage_related_programs

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| conveniopage_id | integer | NO |  |  |
| program_id | uuid | NO |  |  |

## cms_faqindexpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| introduction | text | NO |  |  |
| og_image_id | integer | YES |  |  |

## cms_faqpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| introduction | text | NO |  |  |
| body | jsonb | NO |  |  |
| og_image_id | integer | YES |  |  |

## cms_formfield

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| sort_order | integer | YES |  |  |
| clean_name | character varying | NO |  |  |
| label | character varying | NO |  |  |
| field_type | character varying | NO |  |  |
| required | boolean | NO |  |  |
| choices | text | NO |  |  |
| default_value | text | NO |  |  |
| help_text | character varying | NO |  |  |
| page_id | integer | NO |  |  |

## cms_formpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| to_address | character varying | NO |  |  |
| from_address | character varying | NO |  |  |
| subject | character varying | NO |  |  |
| canonical_url | character varying | NO |  |  |
| introduction | text | NO |  |  |
| thank_you_text | text | NO |  |  |
| linked_program_id | uuid | YES |  |  |
| og_image_id | integer | YES |  |  |

## cms_homepage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| hero_title | character varying | NO |  |  |
| hero_subtitle | text | NO |  |  |
| hero_cta_text | character varying | NO |  |  |
| body | jsonb | YES |  |  |
| hero_cta_link_id | integer | YES |  |  |
| hero_image_id | integer | YES |  |  |
| og_image_id | integer | YES |  |  |

## cms_internationalhomepage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| hero_title | character varying | NO |  |  |
| hero_subtitle | text | NO |  |  |
| introduction | text | NO |  |  |
| body | jsonb | YES |  |  |
| show_stats | boolean | NO |  |  |
| stat_programs_count | integer | NO |  |  |
| stat_countries_count | integer | NO |  |  |
| stat_students_count | integer | NO |  |  |
| stat_institutions_count | integer | NO |  |  |
| hero_image_id | integer | YES |  |  |
| og_image_id | integer | YES |  |  |

## cms_movilidadlandingpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| hero_title | character varying | NO |  |  |
| hero_subtitle | text | NO |  |  |
| introduction | text | NO |  |  |
| body | jsonb | YES |  |  |
| show_quick_links | boolean | NO |  |  |
| show_application_cta | boolean | NO |  |  |
| application_cta_text | character varying | NO |  |  |
| hero_image_id | integer | YES |  |  |
| og_image_id | integer | YES |  |  |

## cms_programindexpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| introduction | text | NO |  |  |
| og_image_id | integer | YES |  |  |

## cms_programpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| introduction | text | NO |  |  |
| body | jsonb | NO |  |  |
| location | character varying | NO |  |  |
| duration | character varying | NO |  |  |
| language | character varying | NO |  |  |
| application_deadline | date | YES |  |  |
| featured_image_id | integer | YES |  |  |
| og_image_id | integer | YES |  |  |
| program_id | uuid | YES |  |  |

## cms_standardpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| introduction | text | NO |  |  |
| body | jsonb | NO |  |  |
| show_sidebar | boolean | NO |  |  |
| sidebar_content | text | NO |  |  |
| og_image_id | integer | YES |  |  |
| featured_image_id | integer | YES |  |  |
| subtitle | character varying | NO |  |  |

## cms_standardpage_related_pages

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| standardpage_id | integer | NO |  |  |
| page_id | integer | NO |  |  |

## cms_testimonialindexpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| introduction | text | NO |  |  |
| og_image_id | integer | YES |  |  |

## cms_testimonialpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_ptr_id | integer | NO |  |  |
| canonical_url | character varying | NO |  |  |
| student_name | character varying | NO |  |  |
| student_major | character varying | NO |  |  |
| exchange_period | character varying | NO |  |  |
| destination_country | character varying | NO |  |  |
| destination_institution | character varying | NO |  |  |
| quote | text | NO |  |  |
| body | jsonb | NO |  |  |
| would_recommend | boolean | NO |  |  |
| og_image_id | integer | YES |  |  |
| program_id | uuid | YES |  |  |
| student_photo_id | integer | YES |  |  |

## data_management_bulkoperation

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| operation_type | character varying | NO |  |  |
| description | text | NO |  |  |
| is_active | boolean | NO |  |  |
| requires_confirmation | boolean | NO |  |  |
| max_records | integer | NO |  |  |
| allowed_roles | jsonb | NO |  |  |
| custom_filters | jsonb | NO |  |  |

## data_management_dataexport

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| model_name | character varying | NO |  |  |
| format | character varying | NO |  |  |
| include_fields | jsonb | NO |  |  |
| filters | jsonb | NO |  |  |
| is_active | boolean | NO |  |  |
| created_by_id | uuid | YES |  |  |

## data_management_dataimport

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| model_name | character varying | NO |  |  |
| format | character varying | NO |  |  |
| field_mapping | jsonb | NO |  |  |
| validation_rules | jsonb | NO |  |  |
| is_active | boolean | NO |  |  |
| created_by_id | uuid | YES |  |  |

## data_management_dataoperationlog

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| operation_type | character varying | NO |  |  |
| model_name | character varying | NO |  |  |
| record_count | integer | NO |  |  |
| operation_details | jsonb | NO |  |  |
| status | character varying | NO |  |  |
| error_message | text | YES |  |  |
| file_path | character varying | YES |  |  |
| user_id | uuid | YES |  |  |

## data_management_datapermission

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| model_name | character varying | NO |  |  |
| permission_type | character varying | NO |  |  |
| custom_filters | jsonb | NO |  |  |
| is_active | boolean | NO |  |  |
| role_id | bigint | NO |  |  |

## data_management_demodataset

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| description | text | NO |  |  |
| data_config | jsonb | NO |  |  |
| is_active | boolean | NO |  |  |
| created_by_id | uuid | YES |  |  |

## django_admin_log

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| action_time | timestamp with time zone | NO |  |  |
| object_id | text | YES |  |  |
| object_repr | character varying | NO |  |  |
| action_flag | smallint | NO |  |  |
| change_message | text | NO |  |  |
| content_type_id | integer | YES |  |  |
| user_id | uuid | NO |  |  |

## django_celery_beat_clockedschedule

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| clocked_time | timestamp with time zone | NO |  |  |

## django_celery_beat_crontabschedule

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| minute | character varying | NO |  |  |
| hour | character varying | NO |  |  |
| day_of_week | character varying | NO |  |  |
| day_of_month | character varying | NO |  |  |
| month_of_year | character varying | NO |  |  |
| timezone | character varying | NO |  |  |

## django_celery_beat_intervalschedule

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| every | integer | NO |  |  |
| period | character varying | NO |  |  |

## django_celery_beat_periodictask

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| name | character varying | NO |  |  |
| task | character varying | NO |  |  |
| args | text | NO |  |  |
| kwargs | text | NO |  |  |
| queue | character varying | YES |  |  |
| exchange | character varying | YES |  |  |
| routing_key | character varying | YES |  |  |
| expires | timestamp with time zone | YES |  |  |
| enabled | boolean | NO |  |  |
| last_run_at | timestamp with time zone | YES |  |  |
| total_run_count | integer | NO |  |  |
| date_changed | timestamp with time zone | NO |  |  |
| description | text | NO |  |  |
| crontab_id | integer | YES |  |  |
| interval_id | integer | YES |  |  |
| solar_id | integer | YES |  |  |
| one_off | boolean | NO |  |  |
| start_time | timestamp with time zone | YES |  |  |
| priority | integer | YES |  |  |
| headers | text | NO |  |  |
| clocked_id | integer | YES |  |  |
| expire_seconds | integer | YES |  |  |

## django_celery_beat_periodictasks

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| ident | smallint | NO |  |  |
| last_update | timestamp with time zone | NO |  |  |

## django_celery_beat_solarschedule

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| event | character varying | NO |  |  |
| latitude | numeric | NO |  |  |
| longitude | numeric | NO |  |  |

## django_content_type

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| app_label | character varying | NO |  |  |
| model | character varying | NO |  |  |

## django_migrations

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| app | character varying | NO |  |  |
| name | character varying | NO |  |  |
| applied | timestamp with time zone | NO |  |  |

## django_session

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| session_key | character varying | NO |  |  |
| session_data | text | NO |  |  |
| expire_date | timestamp with time zone | NO |  |  |

## documents_document

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| file | character varying | NO |  |  |
| is_valid | boolean | NO |  |  |
| validated_at | timestamp with time zone | YES |  |  |
| application_id | uuid | NO |  |  |
| uploaded_by_id | uuid | NO |  |  |
| type_id | bigint | NO |  |  |

## documents_documentcomment

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| text | text | NO |  |  |
| is_private | boolean | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| author_id | uuid | NO |  |  |
| document_id | uuid | NO |  |  |

## documents_documentresubmissionrequest

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| reason | text | NO |  |  |
| resolved | boolean | NO |  |  |
| requested_at | timestamp with time zone | NO |  |  |
| document_id | uuid | NO |  |  |
| requested_by_id | uuid | NO |  |  |

## documents_documenttype

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| name | character varying | NO |  |  |
| description | text | NO |  |  |
| accepted_extensions | character varying | NO |  |  |
| allows_multiple | boolean | NO |  |  |
| faq | text | NO |  |  |
| instructions | text | NO |  |  |
| max_file_size_mb | integer | YES |  |  |
| slug | character varying | YES |  |  |
| submission_mode | character varying | NO |  |  |
| template_file | character varying | YES |  |  |

## documents_documentvalidation

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| result | character varying | NO |  |  |
| details | text | NO |  |  |
| validated_at | timestamp with time zone | NO |  |  |
| document_id | uuid | NO |  |  |
| validator_id | uuid | YES |  |  |

## documents_exchangeagreementdocument

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| category | character varying | NO |  |  |
| title | character varying | NO |  |  |
| file | character varying | NO |  |  |
| notes | text | NO |  |  |
| agreement_id | uuid | NO |  |  |
| supersedes_id | uuid | YES |  |  |
| uploaded_by_id | uuid | YES |  |  |

## dynforms_dynentry

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| created | timestamp with time zone | NO |  |  |
| modified | timestamp with time zone | NO |  |  |
| details | jsonb | YES |  |  |
| is_complete | boolean | NO |  |  |
| form_type_id | bigint | YES |  |  |

## dynforms_formtype

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| created | timestamp with time zone | NO |  |  |
| modified | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| code | character varying | NO |  |  |
| description | text | YES |  |  |
| pages | jsonb | YES |  |  |
| actions | jsonb | YES |  |  |
| header | boolean | NO |  |  |
| help_bar | boolean | NO |  |  |
| wizard | boolean | NO |  |  |

## exchange_agreementcomment

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| text | text | NO |  |  |
| is_private | boolean | NO |  |  |
| agreement_id | uuid | NO |  |  |
| author_id | uuid | NO |  |  |

## exchange_agreementexpirationreminderlog

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| days_before | integer | NO |  |  |
| agreement_end_date | date | NO |  |  |
| agreement_id | uuid | NO |  |  |

## exchange_application

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| submitted_at | timestamp with time zone | YES |  |  |
| withdrawn | boolean | NO |  |  |
| student_id | uuid | NO |  |  |
| status_id | bigint | NO |  |  |
| program_id | uuid | NO |  |  |
| assigned_coordinator_id | uuid | YES |  |  |
| dynamic_form_current_step | character varying | YES |  |  |
| additional_languages_at_apply | jsonb | NO |  |  |
| credits_percent_at_apply | numeric | YES |  |  |
| gpa_at_apply | double precision | YES |  |  |
| grade_scale_at_apply_id | uuid | YES |  |  |
| language_at_apply | character varying | YES |  |  |
| language_level_at_apply | character varying | YES |  |  |
| semester_at_apply | integer | YES |  |  |
| host_institution_id | uuid | YES |  |  |
| host_school_id | uuid | YES |  |  |
| host_academic_program_id | uuid | YES |  |  |
| nomination_rank | integer | YES |  |  |

## exchange_applicationstatus

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| name | character varying | NO |  |  |
| order | integer | NO |  |  |

## exchange_applicationsubjectplanversion

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| version_number | integer | NO |  |  |
| trigger | character varying | NO |  |  |
| payload | jsonb | NO |  |  |
| application_id | uuid | NO |  |  |
| created_by_id | uuid | YES |  |  |

## exchange_applicationsubjectselection

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| home_course_label | character varying | NO |  |  |
| home_course_code | character varying | NO |  |  |
| credits | numeric | YES |  |  |
| notes | text | NO |  |  |
| application_id | uuid | NO |  |  |
| host_subject_id | uuid | YES |  |  |
| custom_code | character varying | NO |  |  |
| custom_name | character varying | NO |  |  |
| custom_credits | numeric | YES |  |  |
| proposed_host_grade_id | uuid | YES |  |  |
| confirmed_host_grade_id | uuid | YES |  |  |
| home_grade_id | uuid | YES |  |  |
| grade_status | character varying | NO |  |  |
| proposed_at | timestamp with time zone | YES |  |  |
| proposed_by_id | uuid | YES |  |  |
| confirmed_at | timestamp with time zone | YES |  |  |
| confirmed_by_id | uuid | YES |  |  |
| confirmation_notes | text | NO |  |  |

## exchange_comment

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| text | text | NO |  |  |
| is_private | boolean | NO |  |  |
| application_id | uuid | NO |  |  |
| author_id | uuid | NO |  |  |

## exchange_eligibilityruleset

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| description | text | NO |  |  |
| schema_version | integer | NO |  |  |
| rules_json | jsonb | NO |  |  |
| is_active | boolean | NO |  |  |

## exchange_exchangeagreement

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| title | character varying | NO |  |  |
| partner_institution_name | character varying | NO |  |  |
| partner_country | character varying | NO |  |  |
| internal_reference | character varying | NO |  |  |
| agreement_type | character varying | NO |  |  |
| start_date | date | YES |  |  |
| end_date | date | YES |  |  |
| status | character varying | NO |  |  |
| notes | text | NO |  |  |
| renewal_follow_up_due | date | YES |  |  |
| renewed_from_id | uuid | YES |  |  |
| application_limit | integer | YES |  |  |
| custom_tags | character varying | NO |  |  |
| language_requirements | jsonb | NO |  |  |
| notify_on_limit_reached | boolean | NO |  |  |
| required_gpa | double precision | YES |  |  |

## exchange_exchangeagreement_programs

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| exchangeagreement_id | uuid | NO |  |  |
| program_id | uuid | NO |  |  |

## exchange_hostacademicprogram

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| code | character varying | NO |  |  |
| is_active | boolean | NO |  |  |
| school_id | uuid | NO |  |  |

## exchange_hostinstitution

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| country | character varying | NO |  |  |
| is_active | boolean | NO |  |  |
| program_id | uuid | NO |  |  |
| grade_scale_id | uuid | YES |  |  |

## exchange_hostschool

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| is_active | boolean | NO |  |  |
| institution_id | uuid | NO |  |  |

## exchange_hostsubject

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| code | character varying | NO |  |  |
| name | character varying | NO |  |  |
| credits | numeric | YES |  |  |
| is_active | boolean | NO |  |  |
| academic_program_id | uuid | YES |  |  |
| institution_id | uuid | NO |  |  |
| school_id | uuid | YES |  |  |

## exchange_partnercontact

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| title | character varying | NO |  |  |
| is_active | boolean | NO |  |  |
| agreement_id | uuid | NO |  |  |
| user_id | uuid | NO |  |  |

## exchange_program

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| description | text | NO |  |  |
| start_date | date | NO |  |  |
| end_date | date | NO |  |  |
| is_active | boolean | NO |  |  |
| min_gpa | double precision | YES |  |  |
| required_language | character varying | YES |  |  |
| recurring | boolean | NO |  |  |
| application_form_id | bigint | YES |  |  |
| auto_reject_ineligible | boolean | NO |  |  |
| max_age | integer | YES |  |  |
| min_age | integer | YES |  |  |
| min_language_level | character varying | YES |  |  |
| application_deadline | date | YES |  |  |
| application_open_date | date | YES |  |  |
| enrollment_capacity | integer | YES |  |  |
| waitlist_when_full | boolean | NO |  |  |
| workflow_version_id | uuid | YES |  |  |
| eligibility_ruleset_id | uuid | YES |  |  |
| min_credits_approved_percent | numeric | YES |  |  |
| min_semester | integer | YES |  |  |

## exchange_program_coordinators

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| program_id | uuid | NO |  |  |
| user_id | uuid | NO |  |  |

## exchange_programdocumentrequirement

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| is_required | boolean | NO |  |  |
| deadline | date | YES |  |  |
| deadline_days_before_program_deadline | integer | YES |  |  |
| instructions_override | text | NO |  |  |
| sort_order | integer | NO |  |  |
| document_type_id | bigint | NO |  |  |
| program_id | uuid | NO |  |  |
| deadline_days_after_program_start | integer | YES |  |  |

## exchange_savedsearch

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| search_type | character varying | NO |  |  |
| filters | jsonb | NO |  |  |
| is_default | boolean | NO |  |  |
| user_id | uuid | NO |  |  |

## exchange_scholarshipaward

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| status | character varying | NO |  |  |
| amount | numeric | YES |  |  |
| currency | character varying | NO |  |  |
| notes | text | NO |  |  |
| decided_at | timestamp with time zone | YES |  |  |
| application_id | uuid | NO |  |  |
| decided_by_id | uuid | YES |  |  |

## exchange_scholarshipdisbursement

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| label | character varying | NO |  |  |
| amount | numeric | YES |  |  |
| due_date | date | YES |  |  |
| paid_at | timestamp with time zone | YES |  |  |
| notes | text | NO |  |  |
| status | character varying | NO |  |  |
| sort_order | integer | NO |  |  |
| award_id | uuid | NO |  |  |

## exchange_timelineevent

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| event_type | character varying | NO |  |  |
| description | text | NO |  |  |
| application_id | uuid | NO |  |  |
| created_by_id | uuid | YES |  |  |

## grades_gradescale

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| code | character varying | NO |  |  |
| description | text | NO |  |  |
| country | character varying | NO |  |  |
| min_value | double precision | NO |  |  |
| max_value | double precision | NO |  |  |
| passing_value | double precision | NO |  |  |
| is_active | boolean | NO |  |  |
| is_reverse_scale | boolean | NO |  |  |

## grades_gradetranslation

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| confidence | double precision | NO |  |  |
| notes | text | NO |  |  |
| created_by_id | uuid | YES |  |  |
| source_grade_id | uuid | NO |  |  |
| target_grade_id | uuid | NO |  |  |

## grades_gradevalue

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| label | character varying | NO |  |  |
| numeric_value | double precision | NO |  |  |
| gpa_equivalent | double precision | NO |  |  |
| min_percentage | double precision | YES |  |  |
| max_percentage | double precision | YES |  |  |
| description | text | NO |  |  |
| order | integer | NO |  |  |
| is_passing | boolean | NO |  |  |
| grade_scale_id | uuid | NO |  |  |

## notifications_notification

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| message | text | YES |  |  |
| is_read | boolean | NO |  |  |
| sent_at | timestamp with time zone | NO |  |  |
| data | jsonb | NO |  |  |
| notification_type | character varying | YES |  |  |
| recipient_id | uuid | YES |  |  |
| title | character varying | YES |  |  |
| action_text | character varying | YES |  |  |
| action_url | character varying | YES |  |  |
| category | character varying | NO |  |  |

## notifications_notificationpreference

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| enabled | boolean | NO |  |  |
| user_id | uuid | NO |  |  |
| type_id | bigint | NO |  |  |

## notifications_notificationroutingoverride

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| kind | character varying | NO |  |  |
| key | character varying | NO |  |  |
| settings_category | character varying | NO |  |  |
| is_active | boolean | NO |  |  |

## notifications_notificationtype

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| name | character varying | NO |  |  |

## notifications_reminder

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| event_type | character varying | NO |  |  |
| event_id | uuid | NO |  |  |
| event_title | character varying | NO |  |  |
| remind_at | timestamp with time zone | NO |  |  |
| sent | boolean | NO |  |  |
| notification_id | uuid | YES |  |  |
| user_id | uuid | NO |  |  |

## taggit_tag

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| name | character varying | NO |  |  |
| slug | character varying | NO |  |  |

## taggit_taggeditem

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| object_id | integer | NO |  |  |
| content_type_id | integer | NO |  |  |
| tag_id | integer | NO |  |  |

## token_blacklist_blacklistedtoken

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| blacklisted_at | timestamp with time zone | NO |  |  |
| token_id | bigint | NO |  |  |

## token_blacklist_outstandingtoken

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| token | text | NO |  |  |
| created_at | timestamp with time zone | YES |  |  |
| expires_at | timestamp with time zone | NO |  |  |
| user_id | uuid | YES |  |  |
| jti | character varying | NO |  |  |

## wagtailadmin_admin

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |

## wagtailadmin_editingsession

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| object_id | character varying | NO |  |  |
| last_seen_at | timestamp with time zone | NO |  |  |
| content_type_id | integer | NO |  |  |
| user_id | uuid | NO |  |  |
| is_editing | boolean | NO |  |  |

## wagtailcore_collection

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| path | character varying | NO |  |  |
| depth | integer | NO |  |  |
| numchild | integer | NO |  |  |
| name | character varying | NO |  |  |

## wagtailcore_collectionviewrestriction

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| restriction_type | character varying | NO |  |  |
| password | character varying | NO |  |  |
| collection_id | integer | NO |  |  |

## wagtailcore_collectionviewrestriction_groups

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| collectionviewrestriction_id | integer | NO |  |  |
| group_id | integer | NO |  |  |

## wagtailcore_comment

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| text | text | NO |  |  |
| contentpath | text | NO |  |  |
| position | text | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| resolved_at | timestamp with time zone | YES |  |  |
| page_id | integer | NO |  |  |
| resolved_by_id | uuid | YES |  |  |
| revision_created_id | integer | YES |  |  |
| user_id | uuid | NO |  |  |

## wagtailcore_commentreply

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| text | text | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| comment_id | integer | NO |  |  |
| user_id | uuid | NO |  |  |

## wagtailcore_groupapprovaltask

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| task_ptr_id | integer | NO |  |  |

## wagtailcore_groupapprovaltask_groups

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| groupapprovaltask_id | integer | NO |  |  |
| group_id | integer | NO |  |  |

## wagtailcore_groupcollectionpermission

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| collection_id | integer | NO |  |  |
| group_id | integer | NO |  |  |
| permission_id | integer | NO |  |  |

## wagtailcore_grouppagepermission

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| group_id | integer | NO |  |  |
| page_id | integer | NO |  |  |
| permission_id | integer | NO |  |  |

## wagtailcore_locale

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| language_code | character varying | NO |  |  |

## wagtailcore_modellogentry

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| label | text | NO |  |  |
| action | character varying | NO |  |  |
| data | jsonb | NO |  |  |
| timestamp | timestamp with time zone | NO |  |  |
| content_changed | boolean | NO |  |  |
| deleted | boolean | NO |  |  |
| object_id | character varying | NO |  |  |
| content_type_id | integer | YES |  |  |
| user_id | uuid | YES |  |  |
| uuid | uuid | YES |  |  |
| revision_id | integer | YES |  |  |

## wagtailcore_page

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| path | character varying | NO |  |  |
| depth | integer | NO |  |  |
| numchild | integer | NO |  |  |
| title | character varying | NO |  |  |
| slug | character varying | NO |  |  |
| live | boolean | NO |  |  |
| has_unpublished_changes | boolean | NO |  |  |
| url_path | text | NO |  |  |
| seo_title | character varying | NO |  |  |
| show_in_menus | boolean | NO |  |  |
| search_description | text | NO |  |  |
| go_live_at | timestamp with time zone | YES |  |  |
| expire_at | timestamp with time zone | YES |  |  |
| expired | boolean | NO |  |  |
| content_type_id | integer | NO |  |  |
| owner_id | uuid | YES |  |  |
| locked | boolean | NO |  |  |
| latest_revision_created_at | timestamp with time zone | YES |  |  |
| first_published_at | timestamp with time zone | YES |  |  |
| live_revision_id | integer | YES |  |  |
| last_published_at | timestamp with time zone | YES |  |  |
| draft_title | character varying | NO |  |  |
| locked_at | timestamp with time zone | YES |  |  |
| locked_by_id | uuid | YES |  |  |
| translation_key | uuid | NO |  |  |
| locale_id | integer | NO |  |  |
| alias_of_id | integer | YES |  |  |
| latest_revision_id | integer | YES |  |  |

## wagtailcore_pagelogentry

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| label | text | NO |  |  |
| action | character varying | NO |  |  |
| data | jsonb | NO |  |  |
| timestamp | timestamp with time zone | NO |  |  |
| content_changed | boolean | NO |  |  |
| deleted | boolean | NO |  |  |
| content_type_id | integer | YES |  |  |
| page_id | integer | NO |  |  |
| revision_id | integer | YES |  |  |
| user_id | uuid | YES |  |  |
| uuid | uuid | YES |  |  |

## wagtailcore_pagesubscription

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| comment_notifications | boolean | NO |  |  |
| page_id | integer | NO |  |  |
| user_id | uuid | NO |  |  |

## wagtailcore_pageviewrestriction

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| password | character varying | NO |  |  |
| page_id | integer | NO |  |  |
| restriction_type | character varying | NO |  |  |

## wagtailcore_pageviewrestriction_groups

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO |  |  |
| pageviewrestriction_id | integer | NO |  |  |
| group_id | integer | NO |  |  |

## wagtailcore_referenceindex

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| object_id | character varying | NO |  |  |
| to_object_id | character varying | NO |  |  |
| model_path | text | NO |  |  |
| content_path | text | NO |  |  |
| content_path_hash | uuid | NO |  |  |
| base_content_type_id | integer | NO |  |  |
| content_type_id | integer | NO |  |  |
| to_content_type_id | integer | NO |  |  |

## wagtailcore_revision

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| content | jsonb | NO |  |  |
| approved_go_live_at | timestamp with time zone | YES |  |  |
| object_id | character varying | NO |  |  |
| user_id | uuid | YES |  |  |
| content_type_id | integer | NO |  |  |
| base_content_type_id | integer | NO |  |  |
| object_str | text | NO |  |  |

## wagtailcore_site

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| hostname | character varying | NO |  |  |
| port | integer | NO |  |  |
| is_default_site | boolean | NO |  |  |
| root_page_id | integer | NO |  |  |
| site_name | character varying | NO |  |  |

## wagtailcore_task

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| name | character varying | NO |  |  |
| active | boolean | NO |  |  |
| content_type_id | integer | NO |  |  |

## wagtailcore_taskstate

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| status | character varying | NO |  |  |
| started_at | timestamp with time zone | NO |  |  |
| finished_at | timestamp with time zone | YES |  |  |
| content_type_id | integer | NO |  |  |
| revision_id | integer | NO |  |  |
| task_id | integer | NO |  |  |
| workflow_state_id | integer | NO |  |  |
| finished_by_id | uuid | YES |  |  |
| comment | text | NO |  |  |

## wagtailcore_uploadedfile

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| file | character varying | NO |  |  |
| for_content_type_id | integer | YES |  |  |
| uploaded_by_user_id | uuid | YES |  |  |

## wagtailcore_workflow

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| name | character varying | NO |  |  |
| active | boolean | NO |  |  |

## wagtailcore_workflowcontenttype

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| content_type_id | integer | NO |  |  |
| workflow_id | integer | NO |  |  |

## wagtailcore_workflowpage

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| page_id | integer | NO |  |  |
| workflow_id | integer | NO |  |  |

## wagtailcore_workflowstate

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| status | character varying | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| current_task_state_id | integer | YES |  |  |
| object_id | character varying | NO |  |  |
| requested_by_id | uuid | YES |  |  |
| workflow_id | integer | NO |  |  |
| content_type_id | integer | NO |  |  |
| base_content_type_id | integer | NO |  |  |

## wagtailcore_workflowtask

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| sort_order | integer | YES |  |  |
| task_id | integer | NO |  |  |
| workflow_id | integer | NO |  |  |

## wagtaildocs_document

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| title | character varying | NO |  |  |
| file | character varying | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| uploaded_by_user_id | uuid | YES |  |  |
| collection_id | integer | NO |  |  |
| file_size | bigint | YES |  |  |
| file_hash | character varying | NO |  |  |

## wagtailembeds_embed

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| url | text | NO |  |  |
| max_width | smallint | YES |  |  |
| type | character varying | NO |  |  |
| html | text | NO |  |  |
| title | text | NO |  |  |
| author_name | text | NO |  |  |
| provider_name | text | NO |  |  |
| thumbnail_url | text | NO |  |  |
| width | integer | YES |  |  |
| height | integer | YES |  |  |
| last_updated | timestamp with time zone | NO |  |  |
| hash | character varying | NO |  |  |
| cache_until | timestamp with time zone | YES |  |  |

## wagtailforms_formsubmission

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| form_data | jsonb | NO |  |  |
| submit_time | timestamp with time zone | NO |  |  |
| page_id | integer | NO |  |  |

## wagtailimages_image

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| title | character varying | NO |  |  |
| file | character varying | NO |  |  |
| width | integer | NO |  |  |
| height | integer | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| focal_point_x | integer | YES |  |  |
| focal_point_y | integer | YES |  |  |
| focal_point_width | integer | YES |  |  |
| focal_point_height | integer | YES |  |  |
| uploaded_by_user_id | uuid | YES |  |  |
| file_size | integer | YES |  |  |
| collection_id | integer | NO |  |  |
| file_hash | character varying | NO |  |  |
| description | character varying | NO |  |  |

## wagtailimages_rendition

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| file | character varying | NO |  |  |
| width | integer | NO |  |  |
| height | integer | NO |  |  |
| focal_point_key | character varying | NO |  |  |
| filter_spec | character varying | NO |  |  |
| image_id | integer | NO |  |  |

## wagtailredirects_redirect

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| old_path | character varying | NO |  |  |
| is_permanent | boolean | NO |  |  |
| redirect_link | character varying | NO |  |  |
| redirect_page_id | integer | YES |  |  |
| site_id | integer | YES |  |  |
| automatically_created | boolean | NO |  |  |
| created_at | timestamp with time zone | YES |  |  |
| redirect_page_route_path | character varying | NO |  |  |

## wagtailsearch_indexentry

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| object_id | character varying | NO |  |  |
| title_norm | double precision | NO |  |  |
| content_type_id | integer | NO |  |  |
| autocomplete | tsvector | NO |  |  |
| title | tsvector | NO |  |  |
| body | tsvector | NO |  |  |

## wagtailseo_seosettings

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| og_meta | boolean | NO |  |  |
| twitter_meta | boolean | NO |  |  |
| twitter_site | character varying | NO |  |  |
| struct_meta | boolean | NO |  |  |
| site_id | integer | NO |  |  |
| struct_org_actions | jsonb | NO |  |  |
| struct_org_address_country | character varying | NO |  |  |
| struct_org_address_locality | character varying | NO |  |  |
| struct_org_address_postal | character varying | NO |  |  |
| struct_org_address_region | character varying | NO |  |  |
| struct_org_address_street | character varying | NO |  |  |
| struct_org_extra_json | text | NO |  |  |
| struct_org_geo_lat | numeric | YES |  |  |
| struct_org_geo_lng | numeric | YES |  |  |
| struct_org_hours | jsonb | NO |  |  |
| struct_org_image_id | integer | YES |  |  |
| struct_org_logo_id | integer | YES |  |  |
| struct_org_name | character varying | NO |  |  |
| struct_org_phone | character varying | NO |  |  |
| struct_org_type | character varying | NO |  |  |
| og_image_default_id | integer | YES |  |  |

## wagtailusers_userprofile

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO |  |  |
| submitted_notifications | boolean | NO |  |  |
| approved_notifications | boolean | NO |  |  |
| rejected_notifications | boolean | NO |  |  |
| user_id | uuid | NO |  |  |
| preferred_language | character varying | NO |  |  |
| current_time_zone | character varying | NO |  |  |
| avatar | character varying | NO |  |  |
| updated_comments_notifications | boolean | NO |  |  |
| dismissibles | jsonb | NO |  |  |
| theme | character varying | NO |  |  |
| density | character varying | NO |  |  |
| contrast | character varying | NO |  |  |

## workflows_workflowdefinition

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| name | character varying | NO |  |  |
| slug | character varying | NO |  |  |
| description | text | NO |  |  |
| is_active | boolean | NO |  |  |

## workflows_workflowevent

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| event_type | character varying | NO |  |  |
| payload | jsonb | NO |  |  |
| actor_id | uuid | YES |  |  |
| instance_id | uuid | NO |  |  |

## workflows_workflowinstance

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| engine_state | jsonb | NO |  |  |
| current_tasks | jsonb | NO |  |  |
| status | character varying | NO |  |  |
| last_event_at | timestamp with time zone | YES |  |  |
| application_id | uuid | NO |  |  |
| workflow_version_id | uuid | NO |  |  |

## workflows_workflowversion

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO |  |  |
| created_at | timestamp with time zone | NO |  |  |
| updated_at | timestamp with time zone | NO |  |  |
| version | integer | NO |  |  |
| status | character varying | NO |  |  |
| bpmn_xml | text | NO |  |  |
| published_at | timestamp with time zone | YES |  |  |
| created_by_id | uuid | YES |  |  |
| definition_id | uuid | NO |  |  |

