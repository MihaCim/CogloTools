create table ps_events
(
	event_id text not null
		constraint ps_events_pk
			primary key,
	timestamp bigint not null,
	data jsonb not null
);

alter table ps_events owner to postgres;

create unique index ps_events_event_id_uindex
	on ps_events (event_id);

