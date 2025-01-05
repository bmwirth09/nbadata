REVOKE ALL ON SCHEMA public FROM public;
CREATE SCHEMA public_access;
CREATE USER public_access_user WITH PASSWORD 'l&JYH!9*@rwmh2629HQ';
GRANT USAGE ON SCHEMA public_access TO public_access_user;
GRANT CONNECT ON DATABASE database_name TO username;
GRANT SELECT ON ALL TABLES IN SCHEMA public_access TO public_access_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public_access GRANT SELECT ON TABLES TO public_access_user;

# removing
ALTER DEFAULT PRIVILEGES IN SCHEMA public_access REVOKE SELECT ON TABLES FROM public_access_user;
REVOKE SELECT ON ALL TABLES IN SCHEMA public_access FROM public_access_user;
REVOKE USAGE ON SCHEMA public_access FROM public_access_user;
DROP USER IF EXISTS public_access_user;