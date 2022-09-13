begin;

--add sql below here
create table migrations.migrations (
  migration_id uuid primary key default uuid_generate_v4(),
  version bigint not null,
  created_at timestamp with time zone not null default now()
);

commit;
