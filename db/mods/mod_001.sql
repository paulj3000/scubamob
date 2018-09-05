alter table account add column "created" datetime NOT NULL;
alter table account add column "modified" datetime NOT NULL;
alter table account add column "account_id" varchar(15) NOT NULL default '0';
alter table account add column "guid" varchar(15) NOT NULL default '0';
alter table account drop column account_id;
