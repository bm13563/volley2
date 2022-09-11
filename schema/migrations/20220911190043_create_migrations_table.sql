begin;

--add sql below here
create table if not exists migrations.migrations (
  id serial primary key,
  version bigint not null,
  created_at timestamp with time zone not null default now()
);

commit;
