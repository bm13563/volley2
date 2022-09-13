begin;

--add sql below here
create table users (
    user_id uuid primary key default uuid_generate_v4(),
    username text not null,
    password text not null,
    created_at timestamp with time zone not null default now(),
    updated_at timestamp with time zone not null default now(),
    properties jsonb,
    unique(username)
);

create index users_username_idx on users (username);

commit;
