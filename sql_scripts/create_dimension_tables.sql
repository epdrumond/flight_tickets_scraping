-- Create the airports table --------------------------
create table airports (
	code varchar(3) not null,
	name varchar(200) not null,
	city varchar(100) not null,
	state varchar(2) not null,
	longitude decimal(9,6) not null,
	latitude decimal(9,6) not null,
	
	constraint airport_pk primary key (code)
);

-- Create the arline companies table ------------------
create table airline_companies (
	code varchar(3) not null,
	name varchar(200) not null,
	
	constraint arline_companies_pk primary key (code)
);