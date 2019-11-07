select * from points.employee;
select * from points.transaction;

insert into points.transaction values (1,('2019-10-25'),50,3,4);
insert into points.transaction values (2,('2019-10-26'),50,3,5);
insert into points.transaction values (3,('2019-10-26'),50,3,6);
insert into points.transaction values (4,('2019-10-27'),50,3,7);
insert into points.transaction values (5,('2019-10-28'),50,4,7);
insert into points.transaction values (6,('2019-10-29'),50,5,7);
insert into points.transaction values (7,('2019-10-29'),50,6,7);
insert into points.transaction values (8,('2019-10-30'),50,6,3);

insert into points.redemption values (1, 20, ('2019-11-01'), 3);
insert into points.redemption values (2, 40, ('2019-11-02'), 3);
insert into points.redemption values (3, 30, ('2019-11-03'), 6);
insert into points.redemption values (4, 10, ('2019-11-01'), 4);
insert into points.redemption values (5, 10, ('2019-11-01'), 6);
